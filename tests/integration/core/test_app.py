from unittest import TestCase

from pyramid import testing


class TestApp(TestCase):
    """
    Tests for including PyramidCMS into a application
    """

    settings = {
        # in-memory database
        'sqlalchemy.url': 'sqlite://',
        'session.secret': 'super-secret-key',
        'session.cookie_httponly': True,
        'session.cookie_secure': False,
    }

    def setUp(self):
        self.config = testing.setUp(settings=self.settings)

    def test_include(self):
        """
        Tests the :func:`pyramidcms.includeme` function.
        """
        self.config.include('pyramidcms')
