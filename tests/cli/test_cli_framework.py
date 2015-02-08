import argparse
from unittest import TestCase
from unittest.mock import Mock, patch

from pyramidcms import cli
from pyramidcms.core.exceptions import CommandError


class CliFrameworkTests(TestCase):
    """
    Unit tests for the pyramid.cli module.
    """

    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('command', type=str, nargs=argparse.REMAINDER)

    def test_get_command(self):
        """
        Unit test for :func:`pyramidcms.cli.get_command`

        The get_command method returns the pcms sub-command, parsed from
        a list of arguments, usually this is the first array item, unless
        the command is "help" in which case it's the next array item.

        Should also raise an exception when "help" is used without
        a command following after.
        """
        # command should be the first argument
        args = self.parser.parse_args(['command1'])
        self.assertEqual(cli.get_command('pcms', args), 'command1')

        # help followed by command should return first argument
        args = self.parser.parse_args(['help', 'command2'])
        self.assertEqual(cli.get_command('pcms', args), 'command2')

        # help without a command should raise CommandError
        args = self.parser.parse_args(['help'])
        with self.assertRaises(CommandError):
            cli.get_command('pcms', args)

    def test_load_command__success(self):
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

        # settings_dict contains the pyramid settings
        settings_dict = {'test_setting': 'setting_value'}

        with patch('importlib.import_module') as patched_import:
            cli.load_command(app, command, settings_dict)

            # We can't use patched_import.call_count here as it will equal 1
            # rather than 2. The mock_calls property seems to also include
            # calls to methods on the Mock object, while call_count doesn't
            # seem to include these so only returns 1.
            self.assertEqual(len(patched_import.mock_calls), 2)

            # The module is dynamically imported from "pyramidcms.commands"
            import_call = patched_import.mock_calls[0]
            import_args = import_call[1]
            self.assertEqual(import_args, ('pyramidcms.commands.command1',))

            # The Command class from the module we just loaded is created
            # We can actually check if Command() was called and the args used.
            new_command_call = patched_import.mock_calls[1]
            new_command_method = new_command_call[0]
            new_command_args = new_command_call[1]
            self.assertEqual(new_command_method, '().Command')
            self.assertEqual(new_command_args, (app, command, settings_dict))

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
