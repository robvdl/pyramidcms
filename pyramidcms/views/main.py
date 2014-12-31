from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.exc import DBAPIError

from pyramidcms.layouts.base import BaseLayout
from pyramidcms.models.auth import User


class MainViews(BaseLayout):

    @view_config(route_name='home', renderer='index.jinja2', permission='create')
    def home(request):
        """
        This is just a placeholder for a dummy homepage and will be removed.
        """
        try:
            user = User.objects.get(username='admin')
        except DBAPIError:
            return Response(conn_err_msg, content_type='text/plain', status_int=500)
        return {'user': user, 'project': 'pyramidcms'}


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_pyramidcms_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
