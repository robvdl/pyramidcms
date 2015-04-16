from sqlalchemy import engine_from_config

from pyramidcms.db import DBSession, Base
from pyramidcms.security import groupfinder, get_current_user, RootFactory


def includeme(config):
    """
    This function initialises PyramidCMS.
    """
    # we can get to the settings object through config.registry
    settings = config.registry.settings

    # initialise SQLAlchemy
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    # pyramidcms dependencies
    config.include('pyramid_jinja2')
    config.include('pyramid_tm')
    config.include('cornice')

    # configure pyramid_jinja2 settings
    config.add_jinja2_search_path('pyramidcms:templates')
    config.add_jinja2_extension('jinja2.ext.with_')

    # this makes request.user available as a lazy loaded property
    config.add_request_method(get_current_user, 'user', reify=True)

    # routes
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.scan()
