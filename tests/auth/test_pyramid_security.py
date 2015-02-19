from unittest import TestCase
from unittest.mock import Mock, patch

from pyramidcms import security


class TestPyramidSecurity(TestCase):

    def test_groupfinder(self):
        """
        Tests the groupfinder function from pyramidcms.security, this should
        return a list of group names prepended with group: and if the user is
        also a superuser, the special group 'superuser' should be there too.
        """
        # generate a mock request object, a user and some groups
        mock_request = Mock()
        mock_request.user.groups = []
        for i in range(1, 3):
            mock_group = Mock()
            mock_group.name = 'Group {}'.format(i)
            mock_request.user.groups.append(mock_group)

        # start with a regular user (non-superuser)
        mock_request.user.superuser = False
        groups = security.groupfinder('test-user', mock_request)
        self.assertListEqual(groups, ['group:Group 1', 'group:Group 2'])

        # now try a superuser
        mock_request.user.superuser = True
        groups = security.groupfinder('test-superuser', mock_request)
        self.assertListEqual(groups, ['group:Group 1', 'group:Group 2', 'superuser'])

    @patch('pyramidcms.security.User')
    def test_get_current_user(self, user_mock):
        # pyramid calls username 'userid'
        mock_request = Mock()
        mock_request.unauthenticated_userid = 'test-user'
        security.get_current_user(mock_request)

        # checks if the function does a query for this user
        user_mock.objects.get.assert_called_once_with(username='test-user')

        # if username is None, the app should not crash
        mock_request.unauthenticated_userid = None
        security.get_current_user(mock_request)
