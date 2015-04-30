import os
import shlex

from subprocess import call

from pyramidcms.cli import BaseCommand


class Command(BaseCommand):
    """
    Management command to open pshell.
    """

    def setup_args(self, parser):
        # optional argument
        parser.add_argument('ini_file', type=str, nargs='?',
                            default='pyramidcms.ini',
                            help='The .ini file argument, \
                            defaults to pyramidcms.ini')

    def load_pshell(self, ini_settings):
        """
        Loads the pshell command with an ini file configuration.
        """
        call(shlex.split('pshell ' + ini_settings))

    def handle(self, args):
        path = os.path.dirname(__file__) + '/../../'
        self.load_pshell(path + args.ini_file.lower())
