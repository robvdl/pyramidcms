import getpass

import re

from pyramidcms.cli import BaseCommand
from pyramidcms.db.models import User


class Command(BaseCommand):
    """
    Creates a superuser, prompting the user for input.
    """

    def get_superuser_details(self):
        """
        Prompts for username, password and email. If no username is
        given then uses system user as default. Password must validate.
        Email can be blank.

        :return: superuser_details
        """

        username = input("Username: (default '" + getpass.getuser() + "')")
        if username is None:
            username = getpass.getuser()

        valid_password = False
        password = ''
        while(not valid_password):
            password = getpass.getpass('Password:')
            confirm_password = getpass.getpass('Repeat password:')
            if password == '' or confirm_password == '':
                print('Error: Password can not be blank.')
            elif password != confirm_password:
                print('Error: Passwords do not match.')
            else:
                valid_password = True

        valid_email = False
        email = ''
        while(not valid_email):
            email = input('Email:')
            match = re.search(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b', email)
            if match or email == '':
                valid_email = True
            else:
                print('Error: Enter a valid email address.')

        superuser_details = { 'username': username, 'password': password, 'email': email }

        return superuser_details

    def create_superuser(self, superuser_details):
        """
        Creates a superuser in the database according to the parameters
        given in superuser_details.

        :param superuser_details:
        """

        username = superuser_details.get('username')
        user = User(username=username,
                    email=superuser_details.get('email'),
                    is_superuser=True)
        user.set_password(superuser_details.get('password'))
        user.save()
        if User.objects.get(username=username) is not None:
            print('Superuser ' + username  + ' created.')

    def handle(self, args):
        superuser_details = self.get_superuser_details()
        self.create_superuser(superuser_details)
