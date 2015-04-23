import argparse
from unittest import TestCase
from unittest.mock import patch, Mock

from pyramidcms import cli
from pyramidcms.core.exceptions import CommandError


class CliFrameworkTests(TestCase):
    """
    Unit tests for the pyramid.cli module.
    """

    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('command', type=str, nargs=argparse.REMAINDER)

        # mock pyramid settings dict
        self.mock_settings = {
            '__file__': 'pyramidcms.ini',
            'test_setting': 'setting_value',
        }

    @patch('importlib.import_module')
    def test_load_command__success(self, mock_import):
        """
        Unit test for :func:`pyramidcms.cli.load_command`

        Test if the command is dynamically imported correctly from the
        :module:`pyramidcms.commands` module, then checks if the Command
        class is constructed correctly.

        This test is done using :module:`unittest.mock`, no actual
        command is being executed during this test.
        """
        app = 'pcms'
        command = 'command1'

        cli.load_command(app, command, self.mock_settings)

        # module is imported, get a reference to mock module
        mock_import.assert_called_once_with('pyramidcms.commands.command1')
        mock_module = mock_import.return_value

        # Command class in mock module is instantiated
        mock_module.Command.assert_called_once_with(app, command, self.mock_settings)

    def test_load_command__import_error(self):
        """
        Unit test for :func:`pyramidcms.cli.load_command`

        Test what happens if the module cannot be imported, this should
        catch the ImportError and raise a CommandError.
        """
        app = 'pcms'
        command = 'command1'

        # settings_dict contains the pyramid settings
        settings_dict = {'test_setting': 'setting_value'}

        # ImportError is caught and CommandError raised
        with patch('importlib.import_module', side_effect=ImportError):
            with self.assertRaises(CommandError):
                cli.load_command(app, command, settings_dict)

    @patch('glob.glob')
    def test_get_command_list(self, glob_mock):
        """
        Unit test for :func:`pyramidcms.cli.get_command_list`

        This should do a directory listing of the "pyramidcms/commands"
        folder, stripping .py file each file and removing __init__.py
        """
        # an example of what glob.glob('pyramidcms/commands/*.py') could return
        glob_mock.return_value = ['/path/file1.py', '/path/file2.py', '/path/__init__.py']
        self.assertListEqual(cli.get_command_list(), ['file1', 'file2'])

    @patch('pyramidcms.cli.get_appsettings')
    @patch('pyramidcms.cli.setup_logging', Mock())
    def test_main(self, mock_get_appsettings):
        """
        Tests the application entry point (main method) of the cli app.

        Most of the functionality has been refactored out to keep the main
        method as small as possible, making it still (somewhat) testable.

        This tests the various code paths the main method can take:

        * Typing "pcms" without anything after it (show global help)
        * Typing "pcms help" but missing the command (raise CommandError)
        * Typing "pcms help command" (show help on a particular command)
        * Typing "pcms command development.ini" (run a command)
        """
        app = 'pcms'
        mock_get_appsettings.return_value = self.mock_settings

        # "pcms" without arguments should show the help page.
        with patch('pyramidcms.cli.show_pcms_help') as help_mock:
            cli.main([app])
            self.assertTrue(help_mock.called)

        # "pcms help" without a command shows help and raises CommandError.
        with patch('pyramidcms.cli.show_pcms_help') as help_mock:
            with self.assertRaises(CommandError):
                cli.main([app, 'help'])
                self.assertTrue(help_mock.called)

        # "pcms help command" will shows help for a specific command.
        with patch('pyramidcms.cli.show_command_help') as help_mock:
            cli.main([app, 'help', 'command1'])
            help_mock.assert_called_once_with(app, 'command1')

        # "pcms command development.ini" should run the command.
        with patch('pyramidcms.cli.setup_db_connection') as db_connect_mock:
            with patch('pyramidcms.cli.run_command') as run_command_mock:
                cli.main([app, 'command2', 'development.ini'])
                db_connect_mock.assert_called_once_with(self.mock_settings)
                run_command_mock.assert_called_once_with(app, 'command2', [], self.mock_settings)

        # "pcms command production.ini arg1 arg2" should capture arguments.
        with patch('pyramidcms.cli.setup_db_connection') as db_connect_mock:
            with patch('pyramidcms.cli.run_command') as run_command_mock:
                cli.main([app, 'command3', 'production.ini', 'arg1', 'arg2'])
                db_connect_mock.assert_called_once_with(self.mock_settings)
                run_command_mock.assert_called_once_with(app, 'command3', ['arg1', 'arg2'], self.mock_settings)

        # "pcms command development.ini" but .ini file does not exist.
        mock_get_appsettings.side_effect = FileNotFoundError
        with self.assertRaises(CommandError):
            cli.main([app, 'command4', 'development.ini'])

        # "pcms command" without an .ini fails argparse and raises SystemExit.
        with self.assertRaises(SystemExit) as cm:
            cli.main([app, 'command5'])
            self.assertEqual(cm.exception.code, 2)
