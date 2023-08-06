import logging
import os
from typing import Text

import pkg_resources
from alembic import command
from alembic.config import Config
from sqlalchemy.orm import Session

import ragex.community.config as rage_x_config

logger = logging.getLogger(__name__)

ALEMBIC_PACKAGE = pkg_resources.resource_filename(
    __name__, "database/schema_migrations"
)


def run_migrations(session: Session) -> None:
    logger.debug("run migrations ... after implement service ")
    # _run_schema_migrations(session)
    #
    # _create_initial_project(session)
    # _create_default_roles(session)
    # _create_default_permissions(session)
    # _create_system_user(session)
    # _generate_chat_token(session)