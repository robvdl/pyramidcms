from pyramidcms.cli import BaseCommand

from subprocess import call

import os

import re


class Command(BaseCommand):

    def parse_url(self):
        connection = dict()
        parameters = re.split(r'[:@/]+', self.settings['sqlalchemy.url'])
        connection.update(dict(dbms=parameters[0], username=parameters[1], host=parameters[3]))
        # Get the port number if available.
        if len(parameters) == 6:
            connection.update(dict(port=parameters[4], database=parameters[5]))
        else:
            connection.update(dict(database=parameters[4]))
        return connection

    def load_dbms_shell(self, connection):
        if connection.get('dbms').startswith('mysql'):
            command = 'mysql -u {username} -h {host} -D {database}'.format(username=connection.get('username'),
                                                                           host=connection.get('host'),
                                                                           database=connection.get('database'))
        elif connection.get('dbms').startswith('postgresql'):
            command = 'psql -U {username} -h {host} -d {database}'.format(username=connection.get('username'),
                                                                          host=connection.get('host'),
                                                                          database=connection.get('database'))
        else:
            command = 'sqlite3 ' + os.path.abspath(os.path.join(__file__, '../..')) + '/' +\
                      connection.get('database') + '.db'

        if 'port' in connection:
            if connection.get('dbms').startswith('mysql'):
                port_arg = ' -P '
            else:
                port_arg = ' -p '
            port_number = port_arg + connection.get('port')
            command.join(port_number)

        call(command, shell=True)

    def handle(self, args):
        connection = self.parse_url()
        self.load_dbms_shell(connection)