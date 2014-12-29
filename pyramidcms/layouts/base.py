from pyramid.decorator import reify


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

    @reify
    def logged_in(self):
        """
        Template property that returns True if a user is logged in.
        """
        return self.request.user is not None

    @reify
    def csrf_token(self):
        return self.session.get_csrf_token()
