from unittest import TestCase
from unittest.mock import Mock

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
