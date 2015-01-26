import re
import os
import signal
from subprocess import call

from pyramidcms.cli import BaseCommand
from pyramidcms.exceptions import CommandError


# Regex to decompose a SQL Alchemy connection URL into it's base components
RE_DB_URL = re.compile(r'''
    ^(?P<dbms>[^:]+)                                # dbms
    ://                                             # ://
    (?P<username>[^:/@]+)?:?(?P<password>[^:/@]+)?  # username:password
    @?                                              # @
    (?P<host>[^:/]+)?:?(?P<port>\d+)?               # host:port
    /                                               # /
    (?P<database>.+)$                               # database
''', re.VERBOSE)


class Command(BaseCommand):
    """
    Management command to open a database shell.

    At the moment only PostgreSQL, MySQL and SQLite are supported.
    """

    def parse_url(self, url):
        match = RE_DB_URL.match(url)
        if match:
            connection = match.groupdict()
            if connection['host'] is None:
                connection['host'] = 'localhost'
            if connection['port'] is not None:
                connection['port'] = int(connection['port'])
            return connection
        else:
            raise CommandError('Failed to parse sqlalchemy.url connection string')

    def load_dbms_shell(self, connection):
        if connection['dbms'].startswith('mysql'):
            # lowercase -p means prompt for password in mysql
            # if you leave it out, it will try to login without password
            command = 'mysql -u {username} -h {host} -D {database} -p'.format(**connection)
        elif connection['dbms'].startswith('postgresql'):
            command = 'psql -U {username} -h {host} -d {database}'.format(**connection)
        elif connection['dbms'].startswith('sqlite'):
            command = 'sqlite3 ' + connection['database']
        else:
            raise CommandError('Unsupported DBMS ' + connection['dbms'])

        if connection['port']:
            if connection['dbms'].startswith('mysql'):
                command += ' -P ' + str(connection['port'])
            elif connection['dbms'].startswith('postgresql'):
                command += ' -p ' + str(connection['port'])
            else:
                print('Dbms not supported.')

        try:
            call(command, shell=True)
        except KeyboardInterrupt:
            os.kill(os.getpid(), signal.SIGTERM)

    def handle(self, args):
        connection = self.parse_url(self.settings['sqlalchemy.url'])
        self.load_dbms_shell(connection)
