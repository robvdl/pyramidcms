from pyramidcms.cli import BaseCommand
from pyramidcms.security import secret_key_generator


class Command(BaseCommand):
    """
    Generate a secret key using os.urandom and encode in hex.

    Does not update the ini file itself, it just prints a key on the screen.
    """

    def handle(self, args):
        print(secret_key_generator(40))
