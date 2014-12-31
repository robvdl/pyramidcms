import os
import sys
import argparse
import importlib


class BaseCommand(object):
    """
    Base class for all management commands, note that the format is a bit
    different from Django which still uses optparse and we use argparse.
    """

    def __init__(self, cli, command):
        self.parser = argparse.ArgumentParser(prog='{} {}'.format(cli, command))
        self.setup_args(self.parser)

    def run(self, *args):
        args = self.parser.parse_args(args)
        self.handle(args)

    def help(self):
        self.parser.print_help()

    def setup_args(self, parser):
        pass

    def handle(self, args):
        pass


def run_command(cli, command, args):
    """
    Import and run a management command, uses importlib.
    """
    module = importlib.import_module('pyramidcms.commands.' + command)
    cmd = module.Command(cli, command)
    cmd.run(*args)


def command_help(cli, command):
    """
    Shows help on a specific command.

    Note that running "pcms command -h" does exactly the same thing.
    """
    module = importlib.import_module('pyramidcms.commands.' + command)
    cmd = module.Command(cli, command)
    cmd.help()


def main(argv=sys.argv):
    """
    The entry point to all management commands.
    """
    # cli holds just the name of the executable
    cli = os.path.basename(os.path.basename(argv[0]))

    # main parser object, we create another one for the command we are running
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str, nargs=argparse.REMAINDER,
        help="The command to run, type {} help <command> for more help.".format(cli))

    args = parser.parse_args(argv[1:])
    if not args.command:
        parser.print_help()
    elif args.command[0] == 'help':
        if len(args.command) == 2:
            command_help(cli, args.command[1])
        else:
            # FIXME: should be a CommandError exception, like Django
            raise ValueError('{} help requires one argument'.format(cli))
    else:
        run_command(cli, args.command[0], args.command[1:])
