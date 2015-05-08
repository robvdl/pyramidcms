from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import Mock

from pyramidcms.db import ModelManager
from pyramidcms.models import auth
from sqlalchemy.orm import Query


class PermissionManagerTests(TestCase):

    def test_list_by_group(self):
        """
        Tests the Permission.objects.list_by_group() method.
        """
        manager = auth.PermissionManager(auth.Permission)
        result = manager.list_by_group()

        # TODO: there must be a better way to test this with some data.
        # This would verify that the query is actually doing the right thing.
        self.assertEqual(type(result), Query)


class PermissionModelTests(TestCase):

    def test_str(self):
        """
        The __str__ method returns the permission name.
        """
        permission = auth.Permission(name='test-permission')
        self.assertEqual(str(permission), 'test-permission')

    def test_manager(self):
        """
        Ensures the Permission model is using the correct manager class.
        """
        # custom manager
        self.assertEqual(type(auth.Permission.objects), auth.PermissionManager)
        self.assertEqual(auth.Permission.objects.model, auth.Permission)


class GroupModelTests(TestCase):

    def test_str(self):
        """
        The __str__ method returns the group name.
        """
        group = auth.Group(name='test-group')
        self.assertEqual(str(group), 'test-group')

    def test_manager(self):
        """
        Checks the manager class.
        """
        # regular manager
        self.assertEqual(type(auth.Group.objects), ModelManager)
        self.assertEqual(auth.Group.objects.model, auth.Group)


class UserModelTests(TestCase):

    def test_str(self):
        """
        Tests the various cases handled by the __str__ method.
        """
        # only the username is present
        user = auth.User(username='some-user')
        self.assertEqual(str(user), user.username)

        # only the first name
        user = auth.User(username='some-user', first_name='First')
        self.assertEqual(str(user), 'First')

        # only the last name
        user = auth.User(username='some-user', last_name='Last')
        self.assertEqual(str(user), 'Last')

        # both the first and last names
        user = auth.User(username='some-user', first_name='First', last_name='Last')
        self.assertEqual(str(user), 'First Last')

    def test_manager(self):
        """
        Checks the manager class.
        """
        # regular manager
        self.assertEqual(type(auth.User.objects), ModelManager)
        self.assertEqual(auth.User.objects.model, auth.User)

    def test_check_password(self):
        """
        Tests the check_password() method.
        """
        user = auth.User(username='some-user')
        user.set_password('testing123')
        self.assertTrue(user.check_password('testing123'))

    def test_set_password(self):
        """
        Tests the set_password() method.
        """
        user = auth.User(username='some-user')
        user.set_password('testing123')
        self.assertNotEqual(user.password, 'testing123')
        self.assertTrue('pbkdf2-sha256' in user.password)

    def test_get_permissions(self):
        """
        Tests the get_permissions() method.
        """
        user = auth.User(username='some-user')
        result = user.get_permissions()

        # TODO: there must be a better way to test this with some data.
        # This would verify that the query is actually doing the right thing.
        self.assertEqual(type(result), Query)

    def test_set_last_login(self):
        """
        Tests that the set_last_login method sets the current date and
        time then calls save() on the model.
        """
        user = auth.User(username='some-user')
        user.save = Mock()
        user.set_last_login()

        # save should have been called
        user.save.assert_called_with()

        # last_login should be within a second of now.
        self.assertAlmostEqual(user.last_login, datetime.now(), delta=timedelta(seconds=1))
