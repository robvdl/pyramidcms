from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config

from pyramidcms.models import DBSession, Base
from pyramidcms.security import groupfinder, get_current_user, RootFactory


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    # initialise SQLAlchemy
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    # setup security policies
    secret_key = settings['session.secret']
    authn_policy = AuthTktAuthenticationPolicy(
        secret_key,
        http_only=True,       # cookie has HTTP_ONLY so isn't available to JS
        callback=groupfinder,
        hashalg='sha512'
    )
    authz_policy = ACLAuthorizationPolicy()

    # FIXME: use something more secure for sessions (Redis or Beaker)
    session_factory = UnencryptedCookieSessionFactoryConfig(
        secret_key,
        cookie_httponly=True  # cookie has HTTP_ONLY so isn't available to JS
    )

    # setup the Configurator
    config = Configurator(
        settings=settings,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
        root_factory=RootFactory,
        session_factory=session_factory
    )

    # static routes, these should be served by nginx or apache in production
    config.add_static_view('static', 'static', cache_max_age=3600)

    # this makes request.user available
    config.add_request_method(get_current_user, 'user', reify=True)

    # routing table
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan()

    # start app
    return config.make_wsgi_app()
