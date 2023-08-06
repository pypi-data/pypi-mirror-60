import logging
import os
import typing
from typing import Text, Tuple, Generator, Dict, List, Set, Any, Optional
from ragex.community.constants import (
    COMMUNITY_PROJECT_NAME,
    COMMUNITY_USERNAME,
    COMMUNITY_TEAM_NAME,
)

from sanic import Sanic
from sqlalchemy.orm import Session

import rasa.cli.utils as rasa_cli_utils
from rasa.core.domain import InvalidDomain
from rasa.nlu.training_data import TrainingData
from rasa.utils.io import read_yaml_file, read_file
from ragex.community import utils
from rasa.utils import common as rasa_utils
from ragex.community import config
from ragex.community.services.user_service import UserService
from ragex.community.utils import run_operation_in_single_sanic_worker
from ragex.community.constants import (
    CONFIG_FILE_METRICS_KEY,
    CONFIG_METRICS_ENABLED,
    CONFIG_METRICS_WELCOME_SHOWN,
    WELCOME_PAGE_URL,
)


logger = logging.getLogger(__name__)


def create_community_user(session: Session, app: Sanic) -> None:
    from rasax.community.constants import (
        COMMUNITY_USERNAME,
        COMMUNITY_TEAM_NAME,
        COMMUNITY_PROJECT_NAME
    )

    from ragex.community.services.role_service import RoleService
    from ragex.community.services.settings_service import SettingsService

    role_service = RoleService(session)
    role_service.init_roles(project_id=COMMUNITY_PROJECT_NAME)

    settings_service = SettingsService(session)
    password = settings_service.get_local_password()

    # only re-assign password in local mode or if it doesn't exist
    if config.LOCAL_MODE or not password:
        password = _initialize_local_password(settings_service)

    user_service = UserService(session)
    user_service.insert_or_update_user(
        COMMUNITY_USERNAME, password, COMMUNITY_TEAM_NAME
    )

    run_operation_in_single_sanic_worker(app, _startup_info)


def _startup_info() -> None:
    """ Shows the login credentials """

    from ragex.community.constants import COMMUNITY_USERNAME

    if not config.LOCAL_MODE:
        rasa_cli_utils.print_success(
            f"Your login password is '{config.rage_x_password}'."
        )
    else:
        server_url = f"http://localhost:{config.self_port}"
        login_url = (
            f"{server_url}/login?username={COMMUNITY_USERNAME}"
            f"&password={config.rage_x_password}"
        )

        rasa_cli_utils.print_success(f"\nthe Server is running at {login_url}\n")

        if config.OPEN_WEB_BROWSER:
            _open_web_browser(login_url)


def _open_web_browser(login_url: Text) -> None:
    """Opens a new tab on the user's preferred web browser and points it to `login_url`.
    Depending on the metrics configuration, a separate tab may be opened as well,
    showing the user a welcome page.

    Args:
        login_url: URL which the tab should be pointed at.
    """

    import webbrowser

    metrics_config = rasa_utils.read_global_config_value(CONFIG_FILE_METRICS_KEY)

    if metrics_config and metrics_config[CONFIG_METRICS_ENABLED]:
        # If the metrics config does not contain CONFIG_METRICS_WELCOME_SHOWN,
        # then the user has upgraded from a previous version of Rasa X (before
        # this config value was introduced). In these cases, assume that the
        # user has already seen the welcome page.
        if not metrics_config.get(CONFIG_METRICS_WELCOME_SHOWN, True):
            webbrowser.open_new_tab(WELCOME_PAGE_URL)

        metrics_config[CONFIG_METRICS_WELCOME_SHOWN] = True
        rasa_utils.write_global_config_value(CONFIG_FILE_METRICS_KEY, metrics_config)

    webbrowser.open_new_tab(login_url)



def _initialize_local_password(settings_service: "SettingsService") -> Text:
    """Update Rage X password.

        Check if `RAGE_X_PASSWORD` environment variable is set, and use it as password.
        Generate new password if it is not set.
    """
    password = os.environ.get("RAGE_X_PASSWORD", "admin1!")

    # update password in config
    config.rage_x_password = password

    # commit password to db
    settings_service.save_local_password(password)

    return password




def _read_data(paths: List[Text]) -> Generator[Tuple[Text, Text], None, None]:
    for filename in paths:
        yield read_file(filename), filename


