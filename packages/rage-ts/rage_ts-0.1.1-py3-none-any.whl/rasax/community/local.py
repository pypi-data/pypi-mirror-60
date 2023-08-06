import argparse
import logging
import os
import signal
import typing
from typing import Text, Tuple, Dict, Any, List, Union, Optional
from rasax.community import config
from rasa.cli.utils import print_success

if typing.TYPE_CHECKING:
    from sanic import Sanic

logger = logging.getLogger(__name__)

LOCAL_DATA_DIR = "data"
LOCAL_DEFAULT_NLU_FILENAME = "nlu.md"
LOCAL_DEFAULT_STORIES_FILENAME = "stories.md"
LOCAL_DOMAIN_PATH = "domain.yml"
LOCAL_MODELS_DIR = "models"
LOCAL_ENDPOINTS_PATH = "endpoints.yml"


def main(
        args: argparse.Namespace,
        project_path: Text,
        data_path: Text,
        token: Optional[Text] = None,
        config_path: Optional[Text] = config.default_config_path,
) -> None:
    """ Start Rage TS """

    print_success("Start Rage Talk Server... 🚀")

    print(args)
    print(project_path)
    print(data_path)
    print(token)
    print(config_path)



