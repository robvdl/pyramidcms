from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

from pyramid.security import Allow, ALL_PERMISSIONS

from pyramidcms import security


class RootFactoryTests(TestCase):
    """
    Tests for the pyramidcms.security.RootFactory class.
    """

    @patch('pyramidcms.security.Permission')
    def test_acl_from_models(self, permission_mock):
        """
        This test checks the code that dynamically builds the list of ACLs
        on the RootFactory class from the database models, which happens on
        every request.

        This happens in the RootFactory class constructor.
        """
        # Returns a generator of tuples: (Mock, Mock)
        # This simulates the (Permission, Group) tuples that get returned
        # by the Permission.objects.list_by_group() query.
        results_generator = ((MagicMock(), MagicMock()) for _ in range(1, 3))
        permission_mock.objects.list_by_group = Mock(return_value=results_generator)

        mock_request = Mock()

        # Call the RootFactory constructor, which is the method under test.
        # The list of ACLs is then updated on RootFactory.__acl__
        security.RootFactory(mock_request)
        acl = security.RootFactory.__acl__

        # The first ACL line gives superusers full access
        self.assertEqual(acl[0], (Allow, 'superuser', ALL_PERMISSIONS))

        # Then follows a list of ACLs that we build from the db
        for ctrl in acl[1:]:
            self.assertEqual(ctrl[0], Allow)
            self.assertTrue(isinstance(ctrl[1], MagicMock))
            self.assertTrue(isinstance(ctrl[2], MagicMock))
