import json
import logging
import os
from contextlib import contextmanager
import typing
from typing import Union, Text, Any, Optional, Dict

from sanic import Sanic
from sanic.request import Request

from sqlalchemy import create_engine, Sequence
from sqlalchemy import event
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from time import sleep

import ragex.community.config as rage_x_config
from ragex.community.constants import REQUEST_DB_SESSION_KEY

if typing.TYPE_CHECKING:
    from sqlite3 import Connection as SQLite3Connection

logger = logging.getLogger(__name__)


def setup_db(app: Sanic, _, is_local=rage_x_config.LOCAL_MODE) -> None:
    """ Create and initialize database """

    logger.debug("Temp DB process pass")


def _sql_query_parameters_from_environment() -> Optional[Dict]:

    # fetch db query dict from environment, needs to be stored as a json dump
    # https://docs.sqlalchemy.org/en/13/core/engines.html#sqlalchemy.engine.url.URL

    # skip if variable is not set
    db_query = os.environ.get("DB_QUERY")
    if not db_query:
        return None
    try:
        return json.loads(db_query)
    except (TypeError, ValueError):
        logger.exception(
            f"Failed to load SQL query dictionary from environment. Expecting a json dump of a dictionary, but found '{db_query}'."
        )
        return None


def get_db_url(is_local: bool = rage_x_config.LOCAL_MODE) -> Union[Text, URL]:
    """ 환경 변수로부터 database connection url를 return """

    # Users can also pass fully specified database urls instead of individual components
    if os.environ.get("DB_URL"):
        return os.environ.get("DB_URL")

    if is_local and os.environ.get("DB_DRIVER") is None:
        return "sqlite:///rage.db"

    # ADMIN 계정명 select
    # from rasax.community.services.user_service import ADMIN

    return URL(
        drivername=os.environ.get("DB_DRIVER", "postgresql"),
        username=os.environ.get("DB_USER", "admin"), #ADMIN 임시 고정 문자열로 처리
        password=os.environ.get("DB_PASSWORD", "password"),
        host=os.environ.get("DB_HIST", "db"),
        port=os.environ.get("DB_PORT", 5432),
        database=os.environ.get("DB_DATABASE", "rage"),
        query=_sql_query_parameters_from_environment(),

    )


def create_session_maker(url: Union[Text, URL]) -> sessionmaker:
    """ Create a new sessionmaker factory
        A sessionmaker factory generates new Session when called
    """
    import sqlalchemy.exc

    # Database might take a while to come up
    while True:
        try:
            # pool_size and max_overflow can be set to control the number of
            # connections that are kept in the connection pool. these parameters
            # are not available for SQLite (local mode)
            if (
                not rage_x_config.LOCAL_MODE
                or os.environ.get("DB_DRIVER") == "postgresql"
            ):
                engine = create_engine(
                    url,
                    pool_size=int(os.environ.get("SQL_POOL_SIZE", "50")),
                    max_overflow=int(os.environ.get("SQL_MAX_OVERFLOW","100")),
                )
            else:
                engine = create_engine(url)
            return sessionmaker(bind=engine)
        except sqlalchemy.exc.OperationalError as e:
            logger.warning(e)
            sleep(5)

@contextmanager
def session_scope():
    """ Provide a transactional scope around a series of operations """

    url = get_db_url(rage_x_config.LOCAL_MODE)
    session = create_session_maker(url)()

    try:
        yield session
        session.commit()
    except Exception as _:
        session.rollback()
        raise
    finally:
        session.close()