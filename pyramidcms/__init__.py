from pyramid.settings import aslist, asbool

from .db import setup_db_connection
from .config import resolve_asset_spec
from .security import get_current_user


def includeme(config):
    """
    This function initialises PyramidCMS.
    """
    # we can get to the settings object through config.registry
    settings = config.registry.settings

    # initialise the database connection
    setup_db_connection(settings)

    # pyramidcms dependencies
    config.include('pyramid_jinja2')
    config.include('pyramid_tm')
    config.include('cornice')

    # configure pyramid_jinja2 settings
    config.add_jinja2_search_path('pyramidcms:templates')
    config.add_jinja2_extension('jinja2.ext.with_')

    # this makes request.user available as a lazy loaded property
    config.add_request_method(get_current_user, 'user', reify=True)

    # reads a list of static dirs from the ini file
    static_dirs = aslist(settings.get('static.dirs', 'pyramidcms:static'))
    static_dirs = [resolve_asset_spec(path_or_spec) for path_or_spec in static_dirs]
    config.registry.settings['static.dirs'] = static_dirs

    # serving static files can be turned off in production
    serve_static_files = asbool(settings.get('static.serve', False))
    config.registry.settings['static.serve'] = serve_static_files

    # routes
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('static', '/static/*subpath')
    config.scan()
