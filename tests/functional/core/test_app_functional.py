from unittest import TestCase

from webtest import TestApp

from pyramidcms.config import setup_configurator
from pyramidcms import models
from pyramidcms.db import DBSession, Base


class AppFunctionalTests(TestCase):
    """
    Functional tests for testing hitting URLs in the application.
    """

    settings = {
        'sqlalchemy.url': 'sqlite://',
        'session.secret': 'super-secret-key',
        'session.cookie_httponly': True,
        'session.cookie_secure': False,
    }

    def setUp(self):
        # create an app for testing, must match app from pyramidcms scaffold.
        app = self._create_app(self.settings)
        self.test_app = TestApp(app)

    def _create_app(self, settings):
        """
        Creates a test app, the app matches the app normally created when
        using the pyramidcms project scaffold.

        The only difference is that we create the models during app startup
        in an in-memory SQLite database.  This is normally handed by
        Alembic migrations.
        """
        config = setup_configurator(settings)
        config.include('pyramidcms')

        # creates all the tables in the in-memory sqlite database
        print('Using models: {}'.format(models.__all__))
        Base.metadata.create_all(DBSession.bind)

        config.scan()
        return config.make_wsgi_app()

    def test_homepage(self):
        """
        Creates an application and try to hit the root url.
        """
        self.test_app.get('/', status=200)
