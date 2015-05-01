from unittest import TestCase

from pyramid import testing
from pyramid.httpexceptions import HTTPBadRequest
from cornice.resource import resource

from pyramidcms.api import ApiBase


@resource(collection_path='/api/group', path='/api/group/{id}')
class MockGroupApi(ApiBase):
    """
    A very simple mock API without any customisations.
    """

    def get_obj_list(self):
        return []


@resource(collection_path='/api/user', path='/api/user/{id}')
class MockUserApi(ApiBase):
    """
    Another mock API, this one has 1000 items and a custom limit.
    """

    class Meta:
        limit = 10

    def get_obj_list(self):
        return range(1000)


class ApiBaseTest(TestCase):
    """
    Tests the API base class by registering some actual mock APIs.
    """

    def test_constructor(self):
        """
        Tests that the api_url property is generated properly when creating
        and instance of an API class.
        """
        request = testing.DummyRequest()
        group_api = MockGroupApi(request)
        user_api = MockUserApi(request)

        self.assertEqual(group_api.request, request)
        self.assertEqual(group_api.api_url, '/api/group')
        self.assertEqual(group_api._meta.limit, 20)

        self.assertEqual(user_api.request, request)
        self.assertEqual(user_api.api_url, '/api/user')
        self.assertEqual(user_api._meta.limit, 10)

    def test_collection_get(self):
        """
        Tests the API collection_get method, which returns a list of items.
        """
        # simple api with an empty list
        request = testing.DummyRequest()
        group_api = MockGroupApi(request)
        data = group_api.collection_get()
        self.assertEqual(type(data), dict)
        self.assertListEqual(sorted(data.keys()), ['items', 'meta'])
        self.assertDictEqual(data['meta'], {
            'limit': 20,
            'next': None,
            'page': 1,
            'num_pages': 1,
            'previous': None,
            'total_count': 0,
        })

        # a slightly more complex api with some items and custom limit, also
        # tests the second page, so we can check the previous page property.
        request = testing.DummyRequest(params={'page': '2'})
        user_api = MockUserApi(request)
        data = user_api.collection_get()
        self.assertEqual(type(data), dict)
        self.assertListEqual(sorted(data.keys()), ['items', 'meta'])
        self.assertDictEqual(data['meta'], {
            'limit': 10,
            'next': '/api/user?page=3',
            'page': 2,
            'num_pages': 100,
            'previous': '/api/user?page=1',
            'total_count': 1000,
        })

        # test with an invalid page number, should raise a 400 bad request
        request = testing.DummyRequest(params={'page': 'invalid'})
        user_api = MockUserApi(request)
        with self.assertRaises(HTTPBadRequest):
            user_api.collection_get()
