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

    def test_get_command_form_args(self):
        """
        Unit test for :func:`pyramidcms.cli.get_command_from_args`

        The get_command_from_args method returns the pcms sub-command, parsed
        from a list of arguments, usually this is the first array item, unless
        the command is "help" in which case it's the next array item.

        Should also raise an exception when "help" is used without
        a command following after.
        """
        # command should be the first argument
        args = self.parser.parse_args(['command1'])
        self.assertEqual(cli.get_command_from_args('pcms', args), 'command1')

        # help followed by command should return first argument
        args = self.parser.parse_args(['help', 'command2'])
        self.assertEqual(cli.get_command_from_args('pcms', args), 'command2')

        # help without a command should raise CommandError
        args = self.parser.parse_args(['help'])
        with self.assertRaises(CommandError):
            cli.get_command_from_args('pcms', args)

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

    @patch('pyramidcms.cli.load_command')
    @patch('pyramidcms.cli.get_appsettings')
    @patch('pyramidcms.cli.setup_logging', Mock())
    def test_main(self, mock_get_appsettings, mock_load_command):
        """
        Tests the application entry point (main method) of the cli app.

        Most of the functionality has been refactored out to keep the main
        method as small as possible, making it still (somewhat) testable.

        This tests the various code paths the main method can take:

        * Typing "pcms" without anything after it (show global help)
        * Typing "pcms help" but missing the command after it
        * Typing "pcms help command" (show help on a particular command)
        * Typing "pcms command" (run a command)
        * Typing "pcms command" but the pyramidcms.ini file does not exist

        When the pyramidcms.ini file does not exist, some commands still need
        to be able to work (namely the createconfig command), in which case
        the cli framework uses a default settings object.
        """
        app = 'pcms'
        mock_get_appsettings.return_value = self.mock_settings

        # Calling pcms without any arguments will show the help page.
        # We aren't testing anything specific here, such as exact screen
        # output, the main thing is to ensure this doesn't crash.
        cli.main([app])

        # "pcms help" without a command raises CommandError
        with self.assertRaises(CommandError):
            cli.main([app, 'help'])

        # "pcms help command" will instantiate Command class and call .help()
        cli.main([app, 'help', 'command1'])
        mock_load_command.assert_called_once_with(app, 'command1', self.mock_settings)
        mock_command = mock_load_command.return_value
        mock_command.help.assert_called_once_with()
        self.assertEqual(mock_command.run.call_count, 0)

        # "pcms command" will instantiate Command class and call .run()
        mock_load_command.reset_mock()
        cli.main([app, 'command2'])
        mock_load_command.assert_called_once_with(app, 'command2', self.mock_settings)
        mock_command = mock_load_command.return_value
        mock_command.run.assert_called_once_with()
        self.assertEqual(mock_command.help.call_count, 0)

        # "pcms command" but pyramidcms.ini file does not exist
        # the command should still work but with a default settings object
        mock_get_appsettings.side_effect = FileNotFoundError
        mock_load_command.reset_mock()
        cli.main([app, 'command3'])
        default_settings = {'__file__': 'pyramidcms.ini'}
        mock_load_command.assert_called_once_with(app, 'command3', default_settings)
