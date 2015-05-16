from .base import Authentication


class SessionAuthentication(Authentication):
    """
    API Authentication class based on the Pyramid session.

    Returns True if a user is logged in.
    """

    def is_authenticated(self, request):
        return request.unauthenticated_userid is not None

    def get_identifier(self, request):
        return request.user.username
