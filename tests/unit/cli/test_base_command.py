from unittest import TestCase
from unittest.mock import Mock, patch

from pyramidcms import cli


class BaseCommandTests(TestCase):

    def test_run(self):
        """
        A simple test that ensures the run method calls handle() in the
        command class that inherits BaseCommand.
        """
        command = cli.BaseCommand('pcms', 'command1', {})

        # create mock and pass through to original method for coverage
        command.handle = Mock(wraps=command.handle)
        command.run()

        # the run method is expected to call handle()
        self.assertTrue(command.handle.called)

    def test_help(self):
        """
        Basic test to check the help() method, mostly just for coverage,
        but it basically it checks that the help() method calls print_help()
        on the argparse object for this command.
        """
        command = cli.BaseCommand('pcms', 'command1', {})
        command.parser = Mock()
        command.help()
        self.assertTrue(command.parser.print_help.called)

    @patch('pyramidcms.cli.run_command')
    def test_call_command(self, run_mock):
        """
        The call_command method can be used to call another command from
        within your command, but without having to call another process
        to do so. The settings dict should be passed to the command called.
        """
        command_args = ['arg1', 'arg2', 'arg3']
        settings = {
            'foo': 'test',
            'bar': 123,
            'baz': True
        }

        command = cli.BaseCommand('pcms', 'command1', settings)

        # the command calls a sub-command
        command.call_command('command2', command_args)

        run_mock.assert_called_once_with('pcms', 'command2', command_args, settings)

        # try without arguments
        run_mock.reset_mock()
        command.call_command('command2')
        run_mock.assert_called_once_with('pcms', 'command2', [], settings)
