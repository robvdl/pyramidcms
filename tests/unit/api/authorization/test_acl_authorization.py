from unittest import TestCase
from unittest.mock import Mock

from pyramid.httpexceptions import HTTPForbidden

from pyramidcms.api.authorization.acl import ACLAuthorization


class ACLAuthorizationTests(TestCase):
    """
    Tests for the ACLAuthorization class.
    """

    def setUp(self):
        self.auth = ACLAuthorization()

    def test_create_list(self):
        mock_request = Mock()
        mock_list = [1, 2, 3]
        self.auth.resource = Mock(request=mock_request)

        # has_permission returns True
        mock_request.has_permission.return_value = True
        self.assertListEqual(self.auth.create_list(mock_list), mock_list)

        # has_permission returns False
        mock_request.has_permission.return_value = False
        with self.assertRaises(HTTPForbidden):
            self.auth.create_list(mock_list)

    def test_create_detail(self):
        mock_request = Mock()
        mock_obj = Mock()
        self.auth.resource = Mock(request=mock_request)

        # has_permission returns True
        mock_request.has_permission.return_value = True
        self.assertTrue(self.auth.create_detail(mock_obj))

        # has_permission returns False
        mock_request.has_permission.return_value = False
        with self.assertRaises(HTTPForbidden):
            self.auth.create_detail(mock_obj)

    def test_read_list(self):
        mock_request = Mock()
        mock_list = [1, 2, 3]
        self.auth.resource = Mock(request=mock_request)

        # has_permission returns True
        mock_request.has_permission.return_value = True
        self.assertListEqual(self.auth.read_list(mock_list), mock_list)

        # has_permission returns False
        mock_request.has_permission.return_value = False
        with self.assertRaises(HTTPForbidden):
            self.auth.read_list(mock_list)

    def test_read_detail(self):
        mock_request = Mock()
        mock_obj = Mock()
        self.auth.resource = Mock(request=mock_request)

        # has_permission returns True
        mock_request.has_permission.return_value = True
        self.assertTrue(self.auth.read_detail(mock_obj))

        # has_permission returns False
        mock_request.has_permission.return_value = False
        with self.assertRaises(HTTPForbidden):
            self.auth.read_detail(mock_obj)

    def test_update_list(self):
        mock_request = Mock()
        mock_list = [1, 2, 3]
        self.auth.resource = Mock(request=mock_request)

        # has_permission returns True
        mock_request.has_permission.return_value = True
        self.assertListEqual(self.auth.update_list(mock_list), mock_list)

        # has_permission returns False
        mock_request.has_permission.return_value = False
        with self.assertRaises(HTTPForbidden):
            self.auth.update_list(mock_list)

    def test_update_detail(self):
        mock_request = Mock()
        mock_obj = Mock()
        self.auth.resource = Mock(request=mock_request)

        # has_permission returns True
        mock_request.has_permission.return_value = True
        self.assertTrue(self.auth.update_detail(mock_obj))

        # has_permission returns False
        mock_request.has_permission.return_value = False
        with self.assertRaises(HTTPForbidden):
            self.auth.update_detail(mock_obj)

    def test_delete_list(self):
        mock_request = Mock()
        mock_list = [1, 2, 3]
        self.auth.resource = Mock(request=mock_request)

        # has_permission returns True
        mock_request.has_permission.return_value = True
        self.assertListEqual(self.auth.delete_list(mock_list), mock_list)

        # has_permission returns False
        mock_request.has_permission.return_value = False
        with self.assertRaises(HTTPForbidden):
            self.auth.delete_list(mock_list)

    def test_delete_detail(self):
        mock_request = Mock()
        mock_obj = Mock()
        self.auth.resource = Mock(request=mock_request)

        # has_permission returns True
        mock_request.has_permission.return_value = True
        self.assertTrue(self.auth.delete_detail(mock_obj))

        # has_permission returns False
        mock_request.has_permission.return_value = False
        with self.assertRaises(HTTPForbidden):
            self.auth.delete_detail(mock_obj)
