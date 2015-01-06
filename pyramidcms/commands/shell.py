import readline
import rlcompleter
from code import InteractiveConsole

from pyramidcms.cli import BaseCommand


class Command(BaseCommand):
    """
    Open an interactive python shell.
    """

    def handle(self, args):
        context = globals().copy()
        context.update(locals())
        readline.set_completer(rlcompleter.Completer(context).complete)
        readline.parse_and_bind('tab: complete')
        shell = InteractiveConsole(context)
        shell.interact()
