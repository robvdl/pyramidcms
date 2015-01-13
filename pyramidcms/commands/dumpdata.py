import sys
import json
import argparse

from pyramidcms.cli import BaseCommand
from pyramidcms.db import models


class Command(BaseCommand):
    """
    Dumps all models to JSON, can be piped into a file to generate fixtures.

    Can also specify a list of models to dump a specific set.
    """

    def setup_args(self, parser):
        parser.add_argument('models', type=str, nargs=argparse.REMAINDER,
                            help='Optional list of models (will dump everything if omitted) ')

    def handle(self, args):
        # This nested list comprehension builds a data structure of all the
        # models, and all records, which can then be converted to JSON.
        json_data = [{'model': m.__name__, 'items': [obj.serialize() for obj in m.objects.all()]} for m in models.__all__]
        json.dump(json_data, sys.stdout, indent=4)
        sys.stdout.write('\n')
