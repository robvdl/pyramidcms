from code import InteractiveConsole

from pyramidcms.cli import BaseCommand
from pyramidcms.db.models import User, Group, Permission


class Command(BaseCommand):

    def handle(self, args):
        console = InteractiveConsole(globals())
        console.interact()
