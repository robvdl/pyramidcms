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
        json_data = []
        for cls in models.__all__:
            model = getattr(models, cls)
            json_data.append({'model': cls, 'objects': [obj.serialize() for obj in model.objects.all()]})

        json.dump(json_data, sys.stdout, indent=4)
        sys.stdout.write('\n')
