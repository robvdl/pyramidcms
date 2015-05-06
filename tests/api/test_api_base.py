from unittest import TestCase
from unittest.mock import Mock

from pyramid import testing
from pyramid.httpexceptions import HTTPBadRequest
from cornice.resource import resource

from pyramidcms.api import ApiBase


@resource(collection_path='/api/simple', path='/api/simple/{id}')
class SimpleApi(ApiBase):
    """
    A very simple API, just an empty list without any customisations.
    """

    def get_obj_list(self):
        return []


@resource(collection_path='/api/number', path='/api/number/{id}')
class NumberApi(ApiBase):
    """
    Another mock API, this one has 1000 items and a custom limit.
    """

    class Meta:
        limit = 10

    def get_obj_list(self):
        return range(1000)

    def get_obj(self, obj_id):
        return obj_id


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
        resource1 = SimpleApi(request)
        resource2 = NumberApi(request)

        self.assertEqual(resource1.request, request)
        self.assertEqual(resource1.api_url, '/api/simple')
        self.assertEqual(resource1._meta.limit, 20)

        self.assertEqual(resource2.request, request)
        self.assertEqual(resource2.api_url, '/api/number')
        self.assertEqual(resource2._meta.limit, 10)

    def test_get_obj_list(self):
        """
        Method should raise NotImplementedError.
        """
        request = testing.DummyRequest()

        # create a direct instance of ApiBase (normally you wouldn't do this)
        resource1 = ApiBase(request)
        with self.assertRaises(NotImplementedError):
            resource1.get_obj_list()

    def test_get_obj(self):
        """
        Method should raise NotImplementedError.
        """
        request = testing.DummyRequest()

        # create a direct instance of ApiBase
        resource1 = ApiBase(request)
        with self.assertRaises(NotImplementedError):
            resource1.get_obj(1)

    def test_hydrate(self):
        """
        Hydrate doesn't really do anything in the ApiBase class,
        it just returns the original object as-is.
        """
        request = testing.DummyRequest()
        resource1 = ApiBase(request)
        test_obj = Mock()
        hydrated = resource1.hydrate(test_obj)
        self.assertEqual(test_obj, hydrated)

    def test_dehydrate(self):
        """
        Dehydrate doesn't really do anything in the ApiBase class,
        it just returns the original object as-is.
        """
        request = testing.DummyRequest()
        resource1 = ApiBase(request)
        test_obj = Mock()
        dehydrated = resource1.dehydrate(test_obj)
        self.assertEqual(test_obj, dehydrated)

    def test_get(self):
        """
        Tests the BaseApi.get() method.
        """
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}
        resource = NumberApi(request)
        self.assertEqual(resource.get(), 10)

    def test_collection_get(self):
        """
        Tests the API collection_get method, which returns a list of items.
        """
        # simple api with an empty list
        request = testing.DummyRequest()
        resource1 = SimpleApi(request)
        data = resource1.collection_get()
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
        resource2 = NumberApi(request)
        data = resource2.collection_get()
        self.assertEqual(type(data), dict)
        self.assertListEqual(sorted(data.keys()), ['items', 'meta'])
        self.assertDictEqual(data['meta'], {
            'limit': 10,
            'next': '/api/number?page=3',
            'page': 2,
            'num_pages': 100,
            'previous': '/api/number?page=1',
            'total_count': 1000,
        })

        # test with an invalid page number, should raise a 400 bad request
        request = testing.DummyRequest(params={'page': 'invalid'})
        resource3 = NumberApi(request)
        with self.assertRaises(HTTPBadRequest):
            resource3.collection_get()
