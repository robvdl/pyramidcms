from unittest import TestCase

from pyramid.testing import DummyRequest

from pyramidcms.api import Api, cms_resource


@cms_resource(resource_name='test')
class MockApi(Api):
    """
    A mock Api resource that doesn't do very much.
    """
    pass


class ApiTests(TestCase):

    def setUp(self):
        request = DummyRequest()
        self.api = MockApi(request)

    def test_resource_name(self):
        self.assertEqual(self.api.resource_name, 'test')

    def test_get_obj(self):
        """
        get_obj() is stubbed.
        """
        self.assertDictEqual(self.api.get_obj(1), {})

    def test_get_obj_list(self):
        """
        get_obj_list() is stubbed.
        """
        self.assertListEqual(self.api.get_obj_list(), [])

    def test_delete_obj(self):
        """
        This method does noting.
        """
        self.api.delete_obj({})

    def test_save_obj(self):
        """
        This method does noting.
        """
        self.api.save_obj({})
