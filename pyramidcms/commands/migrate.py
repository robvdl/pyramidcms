import shlex
import argparse
from subprocess import call

from pyramidcms.cli import BaseCommand


class Command(BaseCommand):
    """
    Runs the alembic migrations for both the cms and the app that is
    using the cms.

    All this really is, is a wrapper around the command::

        alembic -c pyramid.ini upgrade head".

    Nothing special is being done other than run that command, you can also
    run the alembic command directly, but must specify the location of the
    pyramid ini file using the -c argument.
    """

    def setup_args(self, parser):
        # optional arguments passed to alembic
        parser.add_argument('alembic_args', type=str,
                            nargs=argparse.ZERO_OR_MORE, default=['head'],
                            help='Arguments for the "alembic upgrade" command.')

    def get_alembic_command(self):
        """
        Returns the custom alembic command with the -c argument for
        specifying the location of the pyramid ini file.

        :return: alembic command to execute
        """
        return 'alembic -c ' + self.settings['__file__']

    def run_alembic(self, command, args):
        """
        Run the alembic command with the -c argument for specifying
        the location of the pyramid ini file.

        :param command: the alembic command, e.g. "upgrade pyramidcms"
        :param args: arguments from the "pcms migrate" command.
        :return: alembic command, e.g. "alembic -c development.ini"
        """
        alembic_cmd = self.get_alembic_command()
        cmd = shlex.split('{} {}'.format(alembic_cmd, command))
        cmd.extend(args.alembic_args)
        call(cmd)

    def handle(self, args):
        """
        Run the migrations for for pyramidcms and the app.

        The Alembic environment needs the location to the Pyramid ini file,
        because this is where the SQLAlchemy connection string is stored,
        as well as the logging and alembic configuration.
        """
        self.run_alembic('upgrade', args)
