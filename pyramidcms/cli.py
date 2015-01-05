import os
import sys
import argparse
import importlib

from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import engine_from_config

from pyramidcms.db import DBSession
from pyramidcms.exceptions import CommandError


class BaseCommand(object):
    """
    Base class for all management commands, note that the format is a bit
    different from Django which still uses optparse, while we use argparse.

    There is also just one base class to make any management command,
    we don't have a different class for commands without arguments, which
    is what Django does.
    """

    def __init__(self, app, command, settings):
        """
        The default constructor for all management commands.

        This sets up the argparse object for the command itself and
        establishes a connection to the database.

        Note that when you do override the constructor in a command,
        to make sure you still call this constructor.

        :param app: file name of cli executable without the path
        :param command: the name of the command
        :param settings: Pyramid app settings or an empty dict if no ini file.
        """
        self.parser = argparse.ArgumentParser(prog='{} {}'.format(app, command))
        self.settings = settings
        self.init_db()
        self.setup_args(self.parser)

    def init_db(self):
        """
        Establishes a connection to the database when the command
        starts up and the .ini file was loaded successfully.
        """
        # settings is an empty dict if the .ini file doesn't exist,
        # not every command requires the .ini file to exist first.
        if self.settings:
            engine = engine_from_config(self.settings, 'sqlalchemy.')
            DBSession.configure(bind=engine)

    def run(self, *args):
        """
        Run the management command.

        This calls parser.parse_args() then calls the handle() method
        which should be implemented by the command itself.

        :param args: a list of arguments following the command
        """
        args = self.parser.parse_args(args)
        self.handle(args)

    def help(self):
        """
        Print help for this command.

        This is the same as running "pcms <command> -h".
        """
        self.parser.print_help()

    def setup_args(self, parser):
        """
        The setup_args() method gets run before handle is called, it gets
        given an argparse instance so that the sub-classed command can
        add in it's own arguments and options.

        This works considerably different to Django management commands,
        but then this is also based on argparse, while Django uses optparse.

        :param parser: argparse instance object
        """
        pass

    def handle(self, args):
        """
        The handle method is the entry point of the command itself,
        just like a Django management command.  It gets executed by the
        run() method.

        Where it gets considerably different is that args is actually the
        result from running parser.parse_args() from the argparse module.

        This means you can use the dot notation on args, using arguments
        you defined in the setup_args() method.

        :param args: result from running parser.parse_args() from argparse
        """
        pass


def get_command(app, args):
    """
    Returns the command given an argparse instance.

    The command is normally the first argument, unless the command
    was "pcms help command" in which case it's the second argument.

    Running "pcms help command" is actually the same as "pcms command -h".

    :param app: The filename (without path) of the command line app
    :param args: An argparse object containing the parsed arguments
    :returns: The command (a string) that was parsed from args
    """
    if args.command[0] == 'help':
        if len(args.command) == 2:
            return args.command[1]
        else:
            raise CommandError('"{} help" command requires exactly one argument'.format(app))
    else:
        return args.command[0]


def load_command(app, command, settings):
    """
    Given the command as a string, try to load it as as module
    from 'pyramidcms.commands.<command>' and if that was successful,
    instantiates and returns a new instance of that command.

    :param app: The filename (without path) of the command line app
    :param command: The command to load (string)
    :param settings: Pyramid settings object:
    :returns: instance of loaded Command class
    """
    try:
        module = importlib.import_module('pyramidcms.commands.' + command)
    except ImportError:
        raise CommandError('"{} {}" command does not exist.'.format(app, command))

    return module.Command(app, command, settings)


def main(argv=None):
    """
    The entry point to all management commands.

    In a nutshell, this sets up argparse and gets the command from argv,
    then tries to load that module dynamically from pyramidcms.commands.<command>,
    we then get an instance of that command, "cmd" if the module loaded
    successfully.

    If we ran "pcms command ..." then we run "cmd.run(...)" giving it the
    remaining arguments.  See the :meth:`BaseCommand.run()` what happens
    there, but essentially handle() gets called in the command class
    and is given another argparse instance with the remaining arguments.

    If we ran "pcms help command" however, we show the argparse help page
    for that command using "cmd.help()", which is actually just the same
    as running "pcms command -h".

    The pyramidcms.ini file is also loaded and the database connection is
    established before the command is even run, so that when entering the
    handle() method of the command, the database is up and Pyramid settings
    are available under "self.settings".

    :param argv: argv array, if None defaults to sys.argv.
    """
    if argv is None:
        argv = sys.argv

    # app is the name of the cli executable
    app = os.path.basename(os.path.basename(argv[0]))

    # main parser object, we create another one for the command we are running
    parser = argparse.ArgumentParser()
    parser.add_argument('--ini', metavar='ini_file', type=str, nargs=1,
                        default=['pyramidcms.ini'],
                        help='Location of the config file (defaults to pyramidcms.ini)'.format(app))
    parser.add_argument('command', type=str, nargs=argparse.REMAINDER,
                        help='The command to run, type {} help <command> for more help.'.format(app))

    args = parser.parse_args(argv[1:])
    if args.command:
        ini_file = args.ini[0]
        command = get_command(app, args)

        # load .ini file, if this file doesn't exist the
        # settings objects will end up an empty dict
        try:
            setup_logging(ini_file)
            settings = get_appsettings(ini_file)
        except FileNotFoundError:
            settings = {}

        cmd = load_command(app, command, settings)
        if args.command[0] == 'help':
            cmd.help()
        else:
            cmd.run(*args.command[1:])
    else:
        parser.print_help()
