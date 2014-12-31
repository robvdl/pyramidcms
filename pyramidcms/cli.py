import os
import sys
import argparse
import importlib

from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import engine_from_config

from pyramidcms.models import DBSession
from pyramidcms.exceptions import CommandException


class BaseCommand(object):
    """
    Base class for all management commands, note that the format is a bit
    different from Django which still uses optparse and we use argparse.
    """

    def __init__(self, app, command, settings):
        self.parser = argparse.ArgumentParser(prog='{} {}'.format(app, command))
        self.settings = settings
        self.init_db()
        self.setup_args(self.parser)

    def init_db(self):
        # settings is an empty dict if the .ini file doesn't exist,
        # not every command requires the .ini file to exist first.
        if self.settings:
            self.engine = engine_from_config(self.settings, 'sqlalchemy.')
            DBSession.configure(bind=self.engine)
        else:
            self.engine = None

    def run(self, *args):
        args = self.parser.parse_args(args)
        self.handle(args)

    def help(self):
        self.parser.print_help()

    def setup_args(self, parser):
        pass

    def handle(self, args):
        pass


def main(argv=sys.argv):
    """
    The entry point to all management commands.
    """
    # app is the name of the cli executable
    app = os.path.basename(os.path.basename(argv[0]))

    # main parser object, we create another one for the command we are running
    parser = argparse.ArgumentParser()
    parser.add_argument('--ini', metavar='ini_file', type=str, nargs=1, default=['pyramidcms.ini'],
        help="Location of the config file (defaults to pyramidcms.ini)".format(app))
    parser.add_argument('command', type=str, nargs=argparse.REMAINDER,
        help="The command to run, type {} help <command> for more help.".format(app))

    args = parser.parse_args(argv[1:])
    if args.command:
        ini_file = args.ini[0]
        if args.command[0] == 'help':
            if len(args.command) == 2:
                command = args.command[1]
            else:
                raise CommandException('{} help command requires exactly one argument'.format(app))
        else:
            command = args.command[0]

        # load .ini file, if this file doesn't exist the
        # settings objects will end up an empty dict
        try:
            setup_logging(ini_file)
            settings = get_appsettings(ini_file, options={})
        except FileNotFoundError:
            settings = {}

        # load class and either execute command or show help
        module = importlib.import_module('pyramidcms.commands.' + command)
        cmd = module.Command(app, command, settings)
        if args.command[0] == 'help':
           cmd.help()
        else:
           cmd.run(*args.command[1:])
    else:
        parser.print_help()
