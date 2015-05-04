import os

from pyramid.view import view_config
from pyramid.response import FileResponse
from pyramid.httpexceptions import HTTPNotFound


@view_config(route_name='static')
def static_view(request):
    """
    This view serves static files while in development mode, it can deal
    with multiple static folder locations and will serve static files from
    any of the directories listed in the static.dirs setting of the ini file.
    """
    settings = request.registry.settings

    if settings['static.serve']:
        # in development mode, this will serve a static file from any
        # of the locations in the static.dirs setting of the ini file.
        subpath = '/'.join(request.matchdict['subpath'])

        path = None
        for basedir in settings['static.dirs']:
            possible_path = os.path.join(basedir, subpath)
            if os.path.exists(possible_path):
                path = possible_path

        if path:
            return FileResponse(path, request=request)
        else:
            raise HTTPNotFound()
    else:
        # in production static.serve should generally be turned off
        raise HTTPNotFound()
