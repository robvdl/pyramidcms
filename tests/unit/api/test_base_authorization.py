from unittest import TestCase

from pyramid.httpexceptions import HTTPForbidden

from pyramidcms.api.authorization import Authorization, ReadOnlyAuthorization


class AuthorizationTests(TestCase):
    """
    The base Authorization class for API resources allows all operations:
    read, write, update and delete.

    This is not the default authorization class used by API resources
    however, the ReadOnlyAuthorization class is the default class used
    for API resources (unless they specify one), which only allows read.
    """

    def setUp(self):
        self.auth = Authorization()

    def test_read_detail(self):
        test_obj = {'name': 'test'}
        self.assertTrue(self.auth.read_detail(test_obj))

    def test_read_list(self):
        test_list = [1, 2, 3, 4, 5]
        self.assertListEqual(self.auth.read_list(test_list), test_list)

    def test_create_detail(self):
        test_obj = {'name': 'test'}
        self.assertTrue(self.auth.create_detail(test_obj))

    def test_create_list(self):
        test_list = [1, 2, 3, 4, 5]
        self.assertListEqual(self.auth.create_list(test_list), test_list)

    def test_update_detail(self):
        test_obj = {'name': 'test'}
        self.assertTrue(self.auth.update_detail(test_obj))

    def test_update_list(self):
        test_list = [1, 2, 3, 4, 5]
        self.assertListEqual(self.auth.update_list(test_list), test_list)

    def test_delete_detail(self):
        test_obj = {'name': 'test'}
        self.assertTrue(self.auth.delete_detail(test_obj))

    def test_delete_list(self):
        test_list = [1, 2, 3, 4, 5]
        self.assertListEqual(self.auth.delete_list(test_list), test_list)


class ReadOnlyAuthorizationTests(TestCase):
    """
    The ReadOnlyAuthorization class should only allow read operations.
    """

    def setUp(self):
        self.auth = ReadOnlyAuthorization()

    def test_read_detail(self):
        test_obj = {'name': 'test'}
        self.assertTrue(self.auth.read_detail(test_obj))

    def test_read_list(self):
        test_list = [1, 2, 3, 4, 5]
        self.assertListEqual(self.auth.read_list(test_list), test_list)

    def test_create_detail(self):
        test_obj = {'name': 'test'}
        with self.assertRaises(HTTPForbidden):
            self.auth.create_detail(test_obj)

    def test_create_list(self):
        test_list = [1, 2, 3, 4, 5]
        with self.assertRaises(HTTPForbidden):
            self.auth.create_list(test_list)

    def test_update_detail(self):
        test_obj = {'name': 'test'}
        with self.assertRaises(HTTPForbidden):
            self.auth.update_detail(test_obj)

    def test_update_list(self):
        test_list = [1, 2, 3, 4, 5]
        with self.assertRaises(HTTPForbidden):
            self.auth.update_list(test_list)

    def test_delete_detail(self):
        test_obj = {'name': 'test'}
        with self.assertRaises(HTTPForbidden):
            self.auth.delete_detail(test_obj)

    def test_delete_list(self):
        test_list = [1, 2, 3, 4, 5]
        with self.assertRaises(HTTPForbidden):
            self.auth.delete_list(test_list)
