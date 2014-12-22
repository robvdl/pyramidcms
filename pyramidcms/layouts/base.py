from pyramid.decorator import reify
from pyramid.security import authenticated_userid

from pyramidcms.models.auth import User


class BaseLayout(object):
    """
    The BaseLayout class services as the base class for all view classes,
    it provides common properties shared between view classes.
    """

    def __init__(self, request):
        """
        Constructor for all view classes, stores some useful objects
        that can be used in view functions.
        """
        self.request = request
        self.session = request.session
        self.settings = request.registry.settings
        username = authenticated_userid(self.request)
        self.user = User.objects.get(username=username)

    @reify
    def logged_in(self):
        """
        Template property that returns True if a user is logged in.
        """
        return self.user is not None

    @reify
    def csrf_token(self):
        return self.session.get_csrf_token()
