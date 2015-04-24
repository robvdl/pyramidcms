import os
import shlex
from subprocess import call

from pyramidcms.cli import BaseCommand


class Command(BaseCommand):
    """
    Runs the alembic migrations, first for PyramidCMS and then the project
    using the CMS which can have migrations of it's own.
    """

    def handle(self, args):
        """
        Run the migrations for PyramidCMS first, then the project.

        The Alembic environment needs the location to the Pyramid ini file,
        because this is where the SQLAlchemy connection string is stored,
        as well as the logging configuration.

        This is done using the -x argument for the alembic command, which
        allows custom variables to be sent to the env.py.
        """
        # the project PasteDeploy ini file (development.ini or production.ini)
        project_ini = self.settings['__file__']

        # PyramidCMS has an alembic.ini file of it's own, this is for
        # running the migrations included with PyramidCMS itself.
        pcms_alembic_ini = os.path.abspath(os.path.join(os.path.dirname(__file__), '../alembic/alembic.ini'))

        # FIXME: this probably won't work with spaces in the path.
        # We could possibly URL-encode the path to handle spaces, then decode
        # it in env.py to get around this issue.
        command = 'alembic -c {} -x {} upgrade head'.format(pcms_alembic_ini, project_ini)
        call(shlex.split(command), cwd=os.path.dirname(pcms_alembic_ini))

        # TODO: run migrations in project next
