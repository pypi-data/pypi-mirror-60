import argparse
import asyncio  # pytype: disable=pyi-error
import datetime
import decimal
import json
import logging
import os
import random
import re
import string
import tempfile
import typing
from hashlib import md5
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Text,
    TextIO,
    Tuple,
    Union,
    Callable,
    NamedTuple,
    Sequence,
    Collection,
    Awaitable,
)

import dateutil.parser
import isodate
import requests
import ruamel.yaml as yaml
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from rasa.utils.io import DEFAULT_ENCODING
from packaging import version
from ruamel.yaml.comments import CommentedMap
from sanic import response, Sanic
from sanic.request import File, Request
from sanic.response import HTTPResponse
from sanic.views import CompositionView
from sqlalchemy.ext.declarative import DeclarativeMeta

import rasa.cli.utils as rasa_cli_utils
import rasa.utils.common as rasa_utils
import rasa.utils.io as rasa_io_utils
import ragex.community

from ragex.community.constants import CONFIG_FILE_TERMS_KEY, DEFAULT_RAGE_ENVIRONMENT

if typing.TYPE_CHECKING:
    from rasa.utils.endpoints import EndpointConfig

logger = logging.getLogger(__name__)


# SQL query result containing the result and the count
class QueryResult(NamedTuple):
    result: Union[Dict, List[Dict[Text, Any]]]
    count: int

    def __len__(self) -> int:
        """Return query count.

        Implemented here to override tuple's default __len__ which would return
        the amount of elements in the tuple (which could be misleading).
        """
        return self.count


def encode_base64(original: Text, encoding: Text = "utf-8") -> Text:
    """Encodes a string to base64."""

    import base64

    return base64.b64encode(original.encode(encoding)).decode(encoding)


def check_for_updates(timeout: Union[int, float] = 1) -> None:
    """ 새로운 버전이 있는지 현재 설치된 버전과 비교 확인 """

    try:
        rasa_cli_utils.print_info(
            f"Current Rage x Version ({ragex.community.__version__}).\n"
        )
        # current_version = rasax.community.__version__
        # resp = requests.get("http://pypi.rasa.com/api/package/rasa-x", timeout=timeout)
        # resp.raise_for_status()
        # all_versions = [package["version"] for package in resp.json()["packages"]]
        # # Check if there's a stable version newer than the current version
        # newest_stable_version = _get_newer_stable_version(all_versions, current_version)
        # if newest_stable_version != current_version:
        #     rasa_cli_utils.print_info(
        #         f"You are using an outdated version of Rasa X ({current_version}).\n"
        #         f"You should consider upgrading via the command:\npip3 install "
        #         f"--upgrade rasa-x --extra-index-url https://pypi.rasa.com/simple"
        #     )
    except Exception as e:
        logger.debug(
            f"Could not fetch updates from PyPI about newer versions of Rage x: {e}"
        )

def file_as_bytes(path: str) -> bytes:
    """Read in a file as a byte array."""
    with open(path, "rb") as f:
        return f.read()


def update_log_level():
    """Set the log level to log level defined in config."""

    from ragex.community.config import log_level

    logging.basicConfig(level=log_level)
    logging.getLogger("ragex").setLevel(log_level)

    packages = ["rasa", "apscheduler"]
    for p in packages:
        # update log level of package
        logging.getLogger(p).setLevel(log_level)
        # set propagate to 'False' so that logging messages are not
        # passed to the handlers of ancestor loggers.
        logging.getLogger(p).propagate = False

    from sanic.log import logger, error_logger, access_logger

    logger.setLevel(log_level)
    error_logger.setLevel(log_level)
    access_logger.setLevel(log_level)

    logger.propagate = False
    error_logger.propagate = False
    access_logger.propagate = False


def is_git_available() -> bool:
    """Checks if `git` is available in the current environment.

        Returns:
            `True` in case `git` is available, otherwise `False`.
        """

    try:
        import git

        return True
    except ImportError as e:
        logger.error(
            f"An error happened when trying to import the Git library. "
            f"Possible reasons are that Git is not installed or the "
            f"`git` executable cannot be found. 'Integrated Version Control' "
            f"won't be available until this is fixed. Details: {str(e)}"
        )
    return False


def get_file_hash(path: str) -> str:
    """Calculate the md5 hash of a file."""
    return get_text_hash(file_as_bytes(path))



def get_text_hash(text: Optional[Union[str, bytes]]) -> str:
    """Calculate the md5 hash of a string."""
    if text is None:
        text = b""
    elif not isinstance(text, bytes):
        text = text.encode()
    return md5(text).hexdigest()



def filter_fields_from_dict(dictionary: Dict, fields: List[Tuple[Text, bool]]):
    """Gets only the specified fields from a dictionary."""

    # Create a dictionary which resembles our desired structure
    selector_dict = query_result_to_dict([None] * len(fields), fields)

    return common_items(dictionary, selector_dict)



def query_result_to_dict(
    query_result: List[Optional[Text]], fields: List[Tuple[Text, bool]]
) -> Dict[Text, Text]:
    """Convert row to dictionary matching the structure of the field queries.

    A result `["John Doe", 42] and a field query
    `[("username", True), ("user.age", True)]` would be converted to
    `{"username": "John Doe", "user": {"age": 42}}`.

    """
    fields = [k for k, v in fields if v]
    result = {}

    for i, f in enumerate(fields):
        _dot_notation_to_dict(result, f, query_result[i])

    return result



def _dot_notation_to_dict(dictionary: Dict, keys: Text, item: Any) -> None:
    """Creates a dictionary structure matching the given field query."""
    if "." in keys:
        key, rest = keys.split(".", 1)
        if key not in dictionary:
            dictionary[key] = {}
        _dot_notation_to_dict(dictionary[key], rest, item)
    else:
        dictionary[keys] = item


def common_items(d1: Dict, d2: Dict):
    """Recursively get common parts of the dictionaries."""

    return {
        k: common_items(d1[k], d2[k]) if isinstance(d1[k], dict) else d1[k]
        for k in d1.keys() & d2.keys()
    }



# unlike rasa.utils.io's yaml writing method, this one
# uses round_trip_dump() which preserves key order and doesn't print yaml markers
def dump_yaml_to_file(filename: Union[Text, Path], content: Any) -> None:
    """Dump content to yaml."""
    write_text_to_file(filename, dump_yaml(content))


def write_text_to_file(filename: Union[Text, Path], content: Text) -> None:
    """Writes text to a file."""

    from rasa.utils import io as io_utils

    # Create parent directories
    io_utils.create_path(filename)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)




def get_query_selectors(
    table: DeclarativeMeta, fields: List[Text]
) -> List[DeclarativeMeta]:
    """Create select statement based on fields list."""
    if fields:
        return [table.__table__.c[f] for f in fields]
    else:
        return [table]



def get_columns_from_fields(fields: Optional[List[Tuple[Text, bool]]]) -> List[Text]:
    """Get column names from field query which are explicitly included."""
    if fields:
        return [k.rsplit(".", 1)[-1] for k, v in fields if v]
    else:
        return []


def dump_yaml(content: Any) -> Optional[str]:
    """Dump content to yaml."""

    _content = CommentedMap(content)
    return yaml.round_trip_dump(_content, default_flow_style=False)


def run_operation_in_single_sanic_worker(
        app: Sanic, f: Union[Callable[[], Union[None, Awaitable]]]
) -> None:
    """ Run operation 'f' in a single Sanic worker """

    from multiprocessing.sharedctypes import Value
    from ctypes import c_bool

    lock = Value(c_bool, False)

    async def execute():
        if lock.value:
            return


        with lock.get_lock():
            lock.value = True

        if asyncio.iscoroutinefunction(f):
            await f()
        else:
            f()

    app.add_task(execute)