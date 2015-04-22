from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.exc import DBAPIError

from pyramidcms.layouts.base import BaseLayout
from pyramidcms.models import User


class MainViews(BaseLayout):

    @view_config(route_name='home', renderer='index.jinja2', permission='create')
    def home(self):
        """
        This is just a placeholder for a dummy homepage and will be removed.
        """
        try:
            user = User.objects.get(username='admin')
        except DBAPIError:
            return Response('Failed to connect to database', content_type='text/plain', status_int=500)
        return {'user': user, 'project': 'pyramidcms'}
