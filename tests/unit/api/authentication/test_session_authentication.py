from unittest import TestCase
from unittest.mock import Mock

from pyramid import testing

from pyramidcms.api.authentication import SessionAuthentication


class SessionAuthenticationTests(TestCase):
    """
    The SessionAuthentication class authenticates based on the
    Pyramid session.
    """

    def setUp(self):
        self.auth = SessionAuthentication()

    def test_is_authenticated(self):
        """
        The is_authenticated() only returns True if a session is established.
        """
        # user is logged in
        request = testing.DummyRequest()
        request.user = Mock()
        self.assertTrue(self.auth.is_authenticated(request))

        # user is not logged in
        request = testing.DummyRequest()
        request.user = None
        self.assertFalse(self.auth.is_authenticated(request))

    def test_get_identifier(self):
        """
        The get_identifier() method returns the username of the logged in
        user, or None if no user is logged in.
        """
        # user is logged in
        request = testing.DummyRequest()
        request.user = Mock()
        request.user.username = 'john'
        self.assertEqual(self.auth.get_identifier(request), 'john')

        # user is not logged logged in
        request = testing.DummyRequest()
        request.user = None
        self.assertIsNone(self.auth.get_identifier(request))
