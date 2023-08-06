import logging
from typing import Tuple, Dict, Text, Any, List

import jwt
from sanic import Sanic
from sanic_cors import CORS
from sanic_jwt import Initialize, Responses
from sanic_jwt import exceptions

import ragex.community.utils as rage_x_utils
from ragex.community import config, constants
from ragex.community.database.utils import setup_db

from ragex.community.constants import API_URL_PREFIX, REQUEST_DB_SESSION_KEY

logger = logging.getLogger(__name__)


def initialize_app(app: Sanic, class_views: Tuple = ()) -> None:
    Initialize(
        app,
        # service 구현 후 연
        # authenticate=authenticate,
        # add_scopes_to_payload=scope_extender,
        # extend_payload=payload_extender,
        # class_views=class_views,
        # responses_class=ExtendedResponses,
        # retrieve_user=retrieve_user,계
        algorithm=constants.JWT_METHOD,
        private_key=config.jwt_private_key,
        public_key=config.jwt_public_key,
        url_prefix="/api/auth",
        user_id="username",
    )


def configure_app(local_mode: bool = config.LOCAL_MODE) -> Sanic:
    """Create the Sanic app with the endpoint blueprints.

    Args:
        local_mode: 'True' -> local mode , 'False' -> server mode

    Returns:
        Sanic app including the available blueprints

    """

    # sanic-cors shows a DEBUG message for every request which we want to
    # suppress
    logging.getLogger("sanic_cors").setLevel(logging.INFO)
    logging.getLogger("sdf.framework").setLevel(logging.INFO)

    app = Sanic(__name__, configure_logging=config.debug_mode)

    # allow CORS and OPTIONS on Every endpoint
    app.config.CORS_AUTOMATIC_OPTIONS = True
    CORS(
        app,
        expose_headers=["X-Total-Count"],
        max_age=config.SANIC_ACCESS_CONTROL_MAX_AGE
    )

    # Configure Sanic response timeout
    app.config.RESPONSE_TIMEOUT = config.SANIC_RESPONSE_TIMEOUT_IN_SECONDS

    # set JWT expiration time
    app.config.SANIC_JWT_EXPIRATION_DELTA = config.jwt_expiration_time

    # Set up Bluprints ( 차후 등록 )
    # app.blueprint(interface.blueprint())
    # .....

    if not local_mode and rage_x_utils.is_git_available():
        # from rasax.community.api.blueprints import git
        # app.blueprint(git.blueprint(), url_prefix=API_URL_PREFIX)

        pass

    """ before_server_start event가 발생 시 setup_db를 호출 , 비동기로 전환 검토 """
    app.register_listener(setup_db, "before_server_start")

    return app