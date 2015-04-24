"""
Alembic migration environment for PyramidCMS.
"""

import sys
import logging

from sqlalchemy import engine_from_config, pool
from pyramid.paster import get_appsettings, setup_logging

from alembic import context
from pyramidcms import models
from pyramidcms.db import Base


# load the .ini file for the project that is using pyramid from the -x
# argument, this is actually sent by the "pcms migrate" command.
try:
    pyramid_config_file = context.get_x_argument()[0]
except IndexError:
    # The -x argument was not used, alembic was probably executed manually.
    print('Please run alembic using the pcms migrate command instead.')
    sys.exit(2)

alembic_config = context.config
setup_logging(pyramid_config_file)
settings = get_appsettings(pyramid_config_file)
target_metadata = Base.metadata
log = logging.getLogger(__name__)


def run_migrations_offline():
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = settings['sqlalchemy.url']
    context.configure(url=url, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    engine = engine_from_config(
        settings,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata)

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


log.info('PyramidCMS migrations')
log.info('---------------------')
log.info('Using models:')
for cls in models.__all__:
    log.info(' - ' + cls)

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
