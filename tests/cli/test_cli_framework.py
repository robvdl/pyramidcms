import argparse
from unittest import TestCase

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
