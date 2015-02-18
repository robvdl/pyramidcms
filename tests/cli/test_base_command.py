from unittest import TestCase
from unittest.mock import patch

from pyramidcms import cli


class BaseCommandTests(TestCase):

    @patch('pyramidcms.cli.engine_from_config')
    @patch('pyramidcms.cli.DBSession')
    def test_init_db(self, session_mock, engine_mock):
        """
        A command should be able to run whether there is a pyramidcms.ini
        file or not, that is because some commands (namely the createconfig
        command) are used to generate the .ini file so it won't exist yet.

        This test checks that we only try to connect to the db if the key
        "sqlalchemy.url" is present in the Pyramid settings dict, it does
        this by mocking out the SQLAlchemy engine and session objects.

        :param session_mock: mocked SQLAlchemy DBSession
        :param engine_mock: mocked SQLAlchemy engine
        """
        # pyramidcms.ini file exists with db config URL in it
        mock_settings = {'sqlalchemy.url': 'mock:///mockdb'}
        cli.BaseCommand('pcms', 'command1', mock_settings)
        engine_mock.assert_called_once_with(mock_settings, 'sqlalchemy.')
        session_mock.configure.assert_called()

        # reset mocks
        engine_mock.reset_mock()
        session_mock.reset_mock()

        # pyramidcms.ini file doesn't exist or DB url missing
        mock_settings = {}
        cli.BaseCommand('pcms', 'command2', mock_settings)
        self.assertFalse(engine_mock.called)
        self.assertFalse(session_mock.called)
