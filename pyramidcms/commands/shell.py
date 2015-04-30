import os
import shlex
import signal

from subprocess import call

from pyramidcms.cli import BaseCommand


class Command(BaseCommand):
    """
    Management command to open pshell.
    """

    def handle(self, args):
        try:
            call(shlex.split('pshell ' + self.settings['__file__']))
        except KeyboardInterrupt:
            # ctrl+c was pressed in the shell, we need to cleanup
            os.kill(os.getpid(), signal.SIGTERM)
