from pyramid.view import view_config

from pyramidcms.layouts.base import BaseLayout


class BaseViews(BaseLayout):

    @view_config(route_name='home', renderer='index.jinja2')
    def home(self):
        """
        This is just a placeholder for a dummy homepage and will be removed.
        """
        return {'project': 'pyramidcms'}
