class Authentication(object):
    """
    Base class for API authorization, allows everything.
    """

    def is_authenticated(self, request):
        return True

    def get_identifier(self, request):
        return None
