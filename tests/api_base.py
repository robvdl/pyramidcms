from unittest import TestCase

from pyramid import testing
from cornice.resource import resource

from pyramidcms.api import ApiBase


@resource(collection_path='/api/simple', path='/api/simple/{id}')
class SimpleMockApi(ApiBase):
    pass


@resource(collection_path='/api/mock', path='/api/mock/{id}')
class MockApi(ApiBase):

    class Meta:
        limit = 10

    def obj_list(self):
        return range(1000)


class ApiBaseTest(TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.simple_api = SimpleMockApi(self.request)
        self.api = MockApi(self.request)

    def tearDown(self):
        testing.tearDown()

    def test_constructor(self):
        self.assertEqual(self.simple_api.request, self.request)
        self.assertEqual(self.simple_api.api_url, '/api/simple')
        self.assertEqual(self.simple_api.meta.limit, 20)

        self.assertEqual(self.api.request, self.request)
        self.assertEqual(self.api.api_url, '/api/mock')
        self.assertEqual(self.api.meta.limit, 10)

    def test_collection_get(self):
        # simple api with empty list
        data = self.simple_api.collection_get()
        self.assertEqual(type(data), dict)
        self.assertListEqual(sorted(data.keys()), ['items', 'meta'])
        self.assertDictEqual(data['meta'], {
            'limit': 20,
            'next': None,
            'offset': 0,
            'previous': None,
            'total_count': 0,
        })

        # more complex api with more items and custom meta class
        data = self.api.collection_get()
        self.assertEqual(type(data), dict)
        self.assertListEqual(sorted(data.keys()), ['items', 'meta'])
        self.assertDictEqual(data['meta'], {
            'limit': 10,
            'next': '/api/mock?offset=10',
            'offset': 0,
            'previous': None,
            'total_count': 1000,
        })
