from pyramidcms.cli import BaseCommand
from pyramidcms.security import secret_key_generator


class Command(BaseCommand):
    """
    Dumps all models to JSON, can be piped into a file to generate fixtures.

    Can also specify a list of models to dump a specific set.
    """

    def handle(self, args):
        print('The following key can be used as a session_secret:')
        print(secret_key_generator(40))
