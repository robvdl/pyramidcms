import argparse
from unittest import TestCase

from pyramidcms import cli


class CliFrameworkTests(TestCase):
    """
    Unit tests for the pyramid.cli module.
    """

    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('command', type=str, nargs=argparse.REMAINDER)

    def test_get_command(self):
        args = self.parser.parse_args(['command1'])
        self.assertEqual(cli.get_command('pcms', args), 'command1')

        args = self.parser.parse_args(['help', 'command2'])
        self.assertEqual(cli.get_command('pcms', args), 'command2')
