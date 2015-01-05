import os
import codecs

from jinja2 import Template

from pyramidcms.cli import BaseCommand
from pyramidcms.exceptions import CommandError

# location of config templates
CONF_TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../conf'))


class Command(BaseCommand):
    """
    This management command uses the ini template "conf/pyramidcms.ini.jinja2"
    to write a new pyramidcms.ini file either for development or production.
    """

    def setup_args(self, parser):
        # first positional argument is required
        parser.add_argument('environment_type', type=str,
                            help='Type of environment and .ini file to create: dev or prod')

        # second argument is optional
        parser.add_argument('output_file', type=str, nargs='?',
                            default='pyramidcms.ini',
                            help='The output .ini file name, defaults to pyramidcms.ini')

    def secret_key_generator(self, length):
        """
        Generate a new secret key using length given.
        """
        return codecs.encode(os.urandom(length), 'hex').decode('utf-8')

    def handle(self, args):
        with open(os.path.join(CONF_TEMPLATE_DIR, 'pyramidcms.ini.jinja2')) as f:
            template = Template(f.read())

        env = args.environment_type.lower()
        if env == 'dev':
            config = {
                'env': env,
                'db_url': 'sqlite:///%(here)s/pyramidcms.db',
                'secret_key': self.secret_key_generator(40),
                'server_ip': '127.0.0.1',
                'server_port': '8000',
                'num_workers': 1
            }
        elif env == 'prod':
            config = {
                'env': env,
                'db_url': 'sqlite:///%(here)s/pyramidcms.db',
                'secret_key': self.secret_key_generator(40),
                'server_ip': '127.0.0.1',
                'server_port': '8000',
                'num_workers': 4
            }
        else:
            raise CommandError('Unknown environment type: ' + env)

        with open(args.output_file, 'w') as f:
            f.write(template.render(config))

        print('Created {} config file: {}'.format(env, args.output_file))
