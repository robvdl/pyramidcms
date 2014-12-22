from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy import engine_from_config

from pyramidcms.models import DBSession, Base
from pyramidcms.security import groupfinder, RootFactory


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    # initialise SQLAlchemy
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    # setup security policies
    authn_policy = AuthTktAuthenticationPolicy(
        settings['session.secret'],
        http_only=True,
        callback=groupfinder,
        hashalg='sha512'
    )
    authz_policy = ACLAuthorizationPolicy()

    # setup the Configurator
    config = Configurator(
        settings=settings,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
        root_factory=RootFactory,
    )

    # static routes, these should be served by nginx or apache in production
    config.add_static_view('static', 'static', cache_max_age=3600)

    # routing table
    config.add_route('home', '/')
    config.scan()

    # start app
    return config.make_wsgi_app()
