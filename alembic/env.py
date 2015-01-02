"""
Alembic migration environment for PyramidCMS.

Note that there are some differences to a regular Alembic environment,
mainly that we are using two ini files: pyramidcms.ini and alembic.ini

To avoid having to store duplicate settings in both the alembic.ini
and pyramidcms.ini files (for example the SQLAlchemy connection URL and
logging configuration), the settings that were already in pyramidcms.ini
are now loaded from there instead and are removed from alembic.ini.
"""

from alembic import context
from sqlalchemy import engine_from_config, pool
from pyramid.paster import get_appsettings, setup_logging

from pyramidcms.models import Base

# TODO: these still need to be loaded for an import side effect
# we really need to do something about this soon, as it is ugly
from pyramidcms.models.auth import Permission, Group, User

alembic_config = context.config
pyramid_config_file = alembic_config.get_main_option('pyramid_config_file')
setup_logging(pyramid_config_file)
app_settings = get_appsettings(pyramid_config_file, options={})

target_metadata = Base.metadata


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
    url = alembic_config.get_main_option('sqlalchemy.url')
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
        app_settings,
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


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
