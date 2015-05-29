import traceback
import logging
from io import StringIO

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPClientError, HTTPForbidden, HTTPNotFound

from pyramidcms.core.exceptions import get_exception_description, get_http_exception_description

logger = logging.getLogger(__name__)


@view_config(accept='application/json', context=HTTPNotFound, renderer='json')
def api_not_found(context, request):
    """
    Catches 404.

    Note that @notfound_view_config cannot be used here, because we need
    the exception object to get the description and title.

    Note that the errors output from this view matches that what Cornice
    generates, which makes responses the same on the front end.
    """
    request.response.status = context.code

    return {
        'status': 'error',
        'errors': [
            {
                'name': context.title,
                'location': 'url',
                'description': get_http_exception_description(context)
            }
        ]
    }


@view_config(accept='application/json', context=HTTPForbidden, renderer='json')
def api_forbidden(context, request):
    """
    Catches 403, raises 401.

    Note that @forbidden_view_config cannot be used here, because we need
    the exception object to get the description and title.

    Note that the errors output from this view matches that what Cornice
    generates, which makes responses the same on the front end.

    Note that this @forbidden_view_config returns JSON and only gets used
    when calling the API using application/json as the Accept header.
    There is another @forbidden_view_config in auth views that renders the
    login form, but that only gets used if the Accept header is text/html.
    """
    # this actually changes the status code from 403 to 401
    request.response.status = 401

    return {
        'status': 'error',
        'errors': [
            {
                'name': context.title,
                'location': 'url',
                'description': get_http_exception_description(context)
            }
        ]
    }


@view_config(accept='application/json', context=HTTPClientError, renderer='json')
def api_client_error(context, request):
    """
    Catches all HTTP client errors (400, etc), except 404 and 403,
    which Pyramid seems to require handling separately.

    Note that the errors output from this view matches that what Cornice
    generates, which makes responses the same on the front end.
    """
    request.response.status = context.code

    return {
        'status': 'error',
        'errors': [
            {
                'name': context.title,
                'location': 'unknown',
                'description': get_http_exception_description(context)
            }
        ]
    }


@view_config(accept='application/json', context=Exception, renderer='json')
def api_server_error(context, request):
    """
    Catches unhandled exceptions and returns a JSON response.

    If pyramidcms.debug is true in the .ini file, return the traceback
    and exception information.

    If pyramidcms.debug is false in the .ini file, return a generic message.

    Note that the errors output from this view matches that what Cornice
    generates, which makes responses the same on the front end.
    """
    description = get_exception_description(context)
    request.response.status = 500

    # during unit tests, there is an exception but no traceback present.
    if context.__traceback__:
        logger.error('Unhandled exception: {}'.format(description), exc_info=context)
    else:
        logger.error('Unhandled exception: {}'.format(description))

    if request.registry.settings['pyramidcms.debug']:
        # get exception info and traceback if there is one.
        if context.__traceback__:
            with StringIO() as writer:
                traceback.print_tb(context.__traceback__, file=writer)
                tb_lines = writer.getvalue().splitlines()
                tb_lines.insert(0, 'Traceback (most recent call last):')
        else:
            tb_lines = []

        return {
            'status': 'error',
            'errors': [
                {
                    'name': 'Unhandled exception: {}'.format(description),
                    'location': 'unknown',
                    'description': description,
                    'traceback': tb_lines
                }
            ]
        }
    else:
        return {
            'status': 'error',
            'errors': [
                {
                    'name': 'Unexpected error',
                    'location': 'unknown',
                    'description': 'Request cannot be completed'
                }
            ]
        }
