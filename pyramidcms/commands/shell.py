from code import InteractiveConsole

from pyramidcms.cli import BaseCommand


class Command(BaseCommand):
    """
    Open an interactive python shell.
    """

    def handle(self, args):
        console = InteractiveConsole(globals())
        console.interact()
