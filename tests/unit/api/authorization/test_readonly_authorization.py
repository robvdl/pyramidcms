from unittest import TestCase
from unittest.mock import Mock

from pyramid.httpexceptions import HTTPForbidden

from pyramidcms.api.authorization import ReadOnlyAuthorization


class ReadOnlyAuthorizationTests(TestCase):
    """
    The ReadOnlyAuthorization class should only allow read operations.
    """

    def setUp(self):
        self.auth = ReadOnlyAuthorization()
        self.resource = Mock(resource_name='test')

    def test_read_detail(self):
        test_obj = {'name': 'test'}
        self.assertTrue(self.auth.read_detail(test_obj, self.resource))

    def test_read_list(self):
        test_list = [1, 2, 3, 4, 5]
        self.assertListEqual(self.auth.read_list(test_list, self.resource), test_list)

    def test_create_detail(self):
        test_obj = {'name': 'test'}
        with self.assertRaises(HTTPForbidden):
            self.auth.create_detail(test_obj, self.resource)

    def test_create_list(self):
        test_list = [1, 2, 3, 4, 5]
        with self.assertRaises(HTTPForbidden):
            self.auth.create_list(test_list, self.resource)

    def test_update_detail(self):
        test_obj = {'name': 'test'}
        with self.assertRaises(HTTPForbidden):
            self.auth.update_detail(test_obj, self.resource)

    def test_update_list(self):
        test_list = [1, 2, 3, 4, 5]
        with self.assertRaises(HTTPForbidden):
            self.auth.update_list(test_list, self.resource)

    def test_delete_detail(self):
        test_obj = {'name': 'test'}
        with self.assertRaises(HTTPForbidden):
            self.auth.delete_detail(test_obj, self.resource)

    def test_delete_list(self):
        test_list = [1, 2, 3, 4, 5]
        with self.assertRaises(HTTPForbidden):
            self.auth.delete_list(test_list, self.resource)
