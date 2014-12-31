import os
import sys
import codecs

from jinja2 import Template


def secret_key_generator(length):
    """
    Generate a new secret key using length given.
    """
    return codecs.encode(os.urandom(length), 'hex').decode('utf-8')


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: {} <environment_type> [output_file]\n\n'
          'environment_type: this should be dev or prod.\n'
          'output_file: this is optional, it defaults to pyramidcms.ini\n\n'
          '(example: "{} dev")'.format(cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if not len(argv) in (2, 3):
        usage(argv)

    environment_type = argv[1]
    if len(argv) == 3:
        output_file = argv[2]
    else:
        output_file = 'pyramidcms.ini'

    with open('conf/pyramidcms.ini.jinja2') as f:
        template = Template(f.read())

    if environment_type == 'dev':
        config = {
            'debug': True,
            'db_url': 'sqlite:///%(here)s/pyramidcms.db',
            'secret_key': secret_key_generator(40),
            'server_ip': '0.0.0.0',
            'server_port': '8000',
            'num_workers': 1
        }
    else:
        config = {
            'debug': False,
            'db_url': 'sqlite:///%(here)s/pyramidcms.db',
            'secret_key': secret_key_generator(40),
            'server_ip': '127.0.0.1',
            'server_port': '8000',
            'num_workers': 4
        }

    with open(output_file, 'w') as f:
        f.write(template.render(config))

    print('Created config file: ' + output_file)