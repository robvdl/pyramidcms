import re
import os
from subprocess import call

from pyramidcms.cli import BaseCommand
from pyramidcms.exceptions import CommandError


class Command(BaseCommand):

    def parse_url(self):
        connection = {}
        # TODO: if sqlalchemy.url is missing it will crash, we should raise a CommandError
        parameters = re.split(r'[:@/]+', self.settings['sqlalchemy.url'])
        connection.update({'dbms': parameters[0], 'username': parameters[1], 'host':parameters[3]})
        # Get the port number if available.
        if len(parameters) == 6:
            connection.update({'port': parameters[4], 'database': parameters[5]})
        else:
            connection.update({'database': parameters[4]})
        return connection

    def load_dbms_shell(self, connection):
        dbms = connection.get('dbms', '')
        if dbms == 'mysql':
            command = 'mysql -u {username} -h {host} -D {database}'.format(**connection)
        elif dbms == 'postgresql':
            command = 'psql -U {username} -h {host} -d {database}'.format(**connection)
        elif dbms == 'sqlite':
            # FIXME: this is not using os.path.dirname to strip off the filename of this .py file (__file__)
            # FIXME: we shouldn't have to add .db, as the full filename of the database should be in the connection string
            command = 'sqlite3 ' + os.path.abspath(os.path.join(__file__, '../..')) + '/' + \
                      connection.get('database') + '.db'
        else:
            raise CommandError('Unsupported DBMS ' + dbms)

        if 'port' in connection:
            if dbms.startswith('mysql'):
                port_arg = ' -P '
            else:
                port_arg = ' -p '
            port_number = port_arg + connection.get('port')
            command.join(port_number)

        call(command, shell=True)

    def handle(self, args):
        connection = self.parse_url()
        self.load_dbms_shell(connection)
