import os

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.settings import asbool
from pyramid.path import AssetResolver

from pyramidcms.security import groupfinder, RootFactory


def setup_configurator(settings):
    """
    Takes care of some of the session initialisation code so that the app
    using pyramidcms doesn't have to do so.
    """
    # the secret key comes from the PasteDeploy ini file, it is required.
    secret_key = settings['session.secret']
    cookie_httponly = asbool(settings.get('session.cookie_httponly', True))
    cookie_secure = asbool(settings.get('session.cookie_secure', False))

    # setup security policies
    authn_policy = AuthTktAuthenticationPolicy(
        secret_key,
        http_only=cookie_httponly,
        secure=cookie_secure,
        callback=groupfinder,
        hashalg='sha512'
    )

    # FIXME: allow user to choose their own session factory in the ini file
    # the user might prefer to use pyramid_redis_sessions for example...
    session_factory = SignedCookieSessionFactory(
        secret_key,
        httponly=cookie_httponly,
        secure=cookie_secure,
    )

    # setup the Configurator
    return Configurator(
        settings=settings,
        authentication_policy=authn_policy,
        authorization_policy=ACLAuthorizationPolicy(),
        root_factory=RootFactory,
        session_factory=session_factory
    )


def resolve_asset_spec(spec):
    """
    If the path in spec is in the form module:subdir then resolve this
    to the actual full path name, otherwise returns spec unmodified,
    assuming this is a regular path already.

    :param spec: asset specification path
    :return: full resolved path name
    """
    if ':' in spec:
        module, sub_directory = spec.split(':')
        a = AssetResolver(module)
        resolver = a.resolve(os.path.join(sub_directory, ''))
        return resolver.abspath()
    else:
        return spec
