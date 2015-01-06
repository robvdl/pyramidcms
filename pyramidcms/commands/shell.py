from code import InteractiveConsole

import readline

from pyramidcms.cli import BaseCommand


class Command(BaseCommand):
    """
    Open an interactive python shell.
    """

    def handle(self, args):
        shell = InteractiveConsole(globals())
        shell.interact()
