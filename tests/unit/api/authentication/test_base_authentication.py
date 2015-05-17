from unittest import TestCase

from pyramid import testing

from pyramidcms.api.authentication import Authentication


class AuthenticationTests(TestCase):
    """
    The basic Authentication class always allows everything.
    """

    def setUp(self):
        self.auth = Authentication()

    def test_is_authenticated(self):
        """
        The is_authenticated() method always returns True.
        """
        request = testing.DummyRequest()
        self.assertTrue(self.auth.is_authenticated(request))

    def test_get_identifier(self):
        """
        The get_identifier() method just returns None in the base
        Authentication class.
        """
        request = testing.DummyRequest()
        self.assertIsNone(self.auth.get_identifier(request))
