import os
import sys
import glob
import argparse
import importlib

from pyramid.paster import get_appsettings, setup_logging

from pyramidcms.db import setup_db_connection
from pyramidcms.core.exceptions import CommandError


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
        self.parser = argparse.ArgumentParser(prog='{} {} config_uri'.format(app, command))
        self.settings = settings
        self.setup_args(self.parser)

    def run(self, *args):
        """
        Run the management command.

        This calls parser.parse_args() then calls the handle() method
        which should be implemented by the command itself.

        :param args: a list of arguments following the command
        """
        command_args = self.parser.parse_args(args)
        self.handle(command_args)

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


def get_command_from_args(app, args):
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


def get_command_list():
    """
    Returns a list of available commands.

    This is generated by listing all the *.py files in the pyramidcms/commands
    directory and excluding the __init__.py file.

    I have looked at doing this with importlib, but there doesn't seem
    to be a nice way to list all submodules.

    Because of this, we are doing it using the filesystem instead.
    """
    pattern = os.path.join(os.path.dirname(__file__), 'commands/*.py')
    commands = [os.path.basename(f.strip('.py')) for f in glob.glob(pattern)]
    commands.remove('__init__')
    return commands


def show_pcms_help(parser):
    """
    Show help for the pcms cli tool.

    :param parser: :obj:`argparse.ArgumentParser` instance.
    """
    parser.print_help()
    command_list = '\n  '.join(get_command_list())
    print('\navailable commands:\n  {}\n'.format(command_list))


def show_command_help(app, command):
    """
    Show help for the given pcms sub-command.

    :param app: name of command line app, e.g. "pcms"
    :param command: name of the sub-command, e.g. "dbshell"
    """
    cmd = load_command(app, command, {})
    cmd.help()


def run_command(app, command, command_args, settings):
    """
    Run the given pcms sub-command.

    :param app: name of command line app, e.g. "pcms"
    :param command: name of the sub-command, e.g. "dbshell"
    :param settings: pyramid settings dict.
    """
    cmd = load_command(app, command, settings)
    cmd.run(*command_args)


def main(argv=sys.argv):
    """
    The entry point to all management commands.

    If "pcms" is run without any arguments, show general help.

    If "pcms help command" is run, try to load the given command dynamically
    and show the argparse help for that command.

    if "pcms command development.ini" is run, try to load the given command
    and execute it, remaining arguments after the ini file argument are given
    to the commands own argparser instance.

    The database connection is only established when a command is run.

    :param argv: argv array, if None defaults to sys.argv.
    """
    # app is the name of the cli executable
    app = os.path.basename(argv[0])

    # main parser object, we create another one for the command we are running
    parser = argparse.ArgumentParser()

    parser.add_argument('command', type=str,
                        help='The command to run (see available commands below).')
    parser.add_argument('config_uri', type=str,
                        help='The Pyramid ini file to use (PasteDeploy configuration file).')
    parser.add_argument('command_args', type=str, nargs=argparse.REMAINDER,
                        help='Optional command arguments (see: "{} help <command>").'.format(app))

    if len(argv) < 2:
        # "pcms" without arguments, show pcms help
        show_pcms_help(parser)
    else:
        # command help doesn't require an .ini file.
        if argv[1] == 'help':
            if len(argv) == 3:
                # "pcms help command", show command help
                show_command_help(app, argv[2])
            else:
                # "pcms help" with incorrect number of args, show pcms help
                show_pcms_help(parser)
                raise CommandError('"{} help" used without any arguments.'.format(app))
        else:
            # run command, this requires an .ini file.
            args = parser.parse_args(argv[1:])

            try:
                setup_logging(args.config_uri)
                settings = get_appsettings(args.config_uri)
            except FileNotFoundError:
                raise CommandError('Failed to open ini file "{}".'.format(args.config_uri))

            setup_db_connection(settings)
            run_command(app, args.command, args.command_args, settings)
