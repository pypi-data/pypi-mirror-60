import argparse
import asyncio
import logging
import os
import signal
import typing
import ragex.community.utils as rage_x_utils
import ragex.community.initialise as initialise

import ragex.community.jwt
import ragex.community.server as rage_x_server
from typing import Text, Tuple, Dict, Any, List, Union, Optional
from ragex.community import config, metrics, sql_migrations
from rasa.cli.utils import print_success
from ragex.community.constants import (
    COMMUNITY_PROJECT_NAME,
    COMMUNITY_TEAM_NAME,
    COMMUNITY_USERNAME,
    DEFAULT_RAGE_ENVIRONMENT
)
from ragex.community.database.utils import session_scope
from ragex.community.api.app import initialize_app
from sqlalchemy.orm import Session

from rasa.nlu.training_data import TrainingData
from ragex.community.services.domain_service import DomainService
from ragex.community.services.settings_service import (
    SettingsService,
    default_environments_config_local,
)
from ragex.community.services.model_service import ModelService
if typing.TYPE_CHECKING:
    from sanic import Sanic

logger = logging.getLogger(__name__)

LOCAL_DATA_DIR = "data"
LOCAL_DEFAULT_NLU_FILENAME = "nlu.md"
LOCAL_DEFAULT_STORIES_FILENAME = "stories.md"
LOCAL_DOMAIN_PATH = "domain.yml"
LOCAL_MODELS_DIR = "models"
LOCAL_ENDPOINTS_PATH = "endpoints.yml"

def _configure_for_local_server(
        data_path: Text, config_path: Text, token: Optional[Text] = None
) -> None:
    """ 'models' 디렉토리를 만들고 로컬 모드를 위한 변수를 셋팅
    token이 주어진 경우 전역 token으로 셋팅
    """

    if not os.path.isdir(LOCAL_MODELS_DIR):
        os.makedirs(LOCAL_MODELS_DIR)

    if token is not None:
        config.rage_x_token = token

    config.data_dir = data_path
    config.rage_model_dir = LOCAL_MODELS_DIR
    config.project_name = COMMUNITY_PROJECT_NAME
    config.team_name = COMMUNITY_TEAM_NAME
    config.data_dir = LOCAL_DATA_DIR
    config.default_nlu_filename = LOCAL_DEFAULT_NLU_FILENAME
    config.default_stories_filename = LOCAL_DEFAULT_STORIES_FILENAME
    config.default_username = COMMUNITY_USERNAME
    config.default_domain_path = LOCAL_DOMAIN_PATH
    config.default_config_path = config_path
    config.endpoints_path = LOCAL_ENDPOINTS_PATH

def main(
        args: argparse.Namespace,
        project_path: Text,
        data_path: Text,
        token: Optional[Text] = None,
        config_path: Optional[Text] = config.default_config_path,
) -> None:
    """ Start Rage TS """

    print(args)
    print(project_path)
    print(data_path)
    print(token)
    print(config_path)

    """ Start Rage x in local mode """

    """ version check """
    rage_x_utils.check_for_updates()

    print_success("Start Rage Talk Server... 🚀")

    """ rage_x_port 셋팅"""
    config.self_port = args.rasa_x_port

    """ rasa 모듈로 받은 정보 셋팅"""
    _configure_for_local_server(data_path, config_path, token)

    ragex.community.jwt.initialise_jwt_keys()

    """ jwt 확인용 - 추후 삭제 """
    print(config.jwt_public_key)
    print(config.jwt_private_key)

    app = rage_x_server.configure_app()

    with session_scope() as session:
        auth_endpoints = _enable_development_mode_and_get_additional_auth_endpoints(app)
        initialize_app(app, class_views=auth_endpoints)

        sql_migrations.run_migrations(session)

        initialise.create_community_user(session, app)

        _initialize_with_local_data(
            project_path, data_path, session, args.port, config_path
        )

        metrics.track(metrics.LOCAL_START_EVENT)

    # this needs to run after initial database structures are created
    # otherwise projects assigned to events won't be present
    _start_event_service()

    rage_x_utils.run_operation_in_single_sanic_worker(
        app, metrics.track_status_periodically
    )

    app.run(
        host="0.0.0.0",
        port=config.self_port,
        auto_reload=os.environ.get("SANIC_AUTO_RELOAD"),
        access_log=False
    )



def _event_service(metrics_collection_config: Dict[Text, Any], endpoints_path: Text):
    """Start the event service."""
    # noinspection PyUnresolvedReferences
    from rasax.community.services import event_service

    # Set the metrics collection config on this new process
    config.metrics_collection_config = metrics_collection_config

    # set endpoints path variable in this process
    config.endpoints_path = endpoints_path

    def signal_handler(sig, frame):
        print("Stopping event service.")
        os.kill(os.getpid(), signal.SIGTERM)

    signal.signal(signal.SIGINT, signal_handler)

    event_service.main(should_run_liveness_endpoint=False)


def _start_event_service():
    """ Run the event service in a separate process. """

    import multiprocessing

    ctx = multiprocessing.get_context("spawn")  # pytype: disable=module-attr

    p = ctx.Process(
        target=_event_service,
        args=(config.metrics_collection_config, config.endpoints_path),
        daemon=True,
    )
    p.start()



def check_license_and_metrics(args):
    """Ask the user to accept terms and conditions. If already accepted, skip it."""
    # if not rasa_x_utils.are_terms_accepted():
    #     rasa_x_utils.accept_terms_or_quit(args)

    metrics.initialize_configuration_from_file(args.no_prompt)


def _enable_development_mode_and_get_additional_auth_endpoints(
        app: "Sanic",
) -> Union[Tuple[()], Tuple[Text, Any]]:
    """Enable development mode if Rasa X EE is installed.

     Configures enterprise endpoints and returns additional authentication
     endpoints if possible.

     Args:
         app: Sanic app to configure.

     Returns:
         Tuple of authentication endpoints if Rasa X EE is installed and
         Rasa X is run in development, otherwise an empty tuple.

     """
    return ()



def _initialize_with_local_data(
    project_path: Text,
    data_path: Text,
    session: Session,
    rasa_port: Union[int, Text],
    config_path: Text,
) -> Tuple[Dict[Text, Any], List[Dict[Text, Any]], TrainingData]:

    settings_service = SettingsService(session)
    default_env = default_environments_config_local(rasa_port)
    settings_service.save_environments_config(
        COMMUNITY_PROJECT_NAME, default_env.get("environments")
    )

    loop = asyncio.get_event_loop()
    # inject data
    domain, story_blocks, nlu_data = loop.run_until_complete(
        ragex.community.initialise.inject_files_from_disk(
            project_path, data_path, session, config_path=config_path
        )
    )

    # discover model
    model_service = ModelService(LOCAL_MODELS_DIR, session, DEFAULT_RAGE_ENVIRONMENT)
    model_service.discover_models_on_init(sleep_in_seconds=1)

    loop.run_until_complete(model_service.mark_latest_as_production())

    # dump domain once
    domain_service = DomainService(session)
    domain_service.dump_domain()
    return domain, story_blocks, nlu_data

