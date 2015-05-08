from unittest import TestCase

from pyramid import testing


class AppIntegrationTests(TestCase):
    """
    Integration tests for including PyramidCMS into your application
    """

    settings = {
        # in-memory database
        'sqlalchemy.url': 'sqlite://',
        'session.secret': 'super-secret-key',
        'session.cookie_httponly': True,
        'session.cookie_secure': False,
    }

    def setUp(self):
        """
        Sets up an application registry.
        """
        self.config = testing.setUp(settings=self.settings)

    def test_include(self):
        """
        Tests the :func:`pyramidcms.includeme` function.
        """
        self.config.include('pyramidcms')
