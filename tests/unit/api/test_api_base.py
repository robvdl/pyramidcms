from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock, PropertyMock

from pyramid import testing
from pyramid.httpexceptions import HTTPBadRequest, HTTPForbidden, HTTPNotFound,\
    HTTPConflict

from pyramidcms.api import ApiBase, Bundle, cms_resource, get_global_acls
from pyramidcms.api.authorization import Authorization
from pyramidcms.core.messages import NOT_AUTHORIZED, NOT_AUTHENTICATED


class MockObject(object):
    """
    A Mock object used by the NumberApi test resource.
    """

    def __init__(self, data):
        # adding an id is used by API POST test, this wouldn't normally happen
        if 'id' not in data:
            data['id'] = 10

        for key, val in data.items():
            setattr(self, key, val)


@cms_resource(resource_name='simple')
class MockSimpleApi(ApiBase):
    """
    A very simple API, just an empty list without any customisations.
    """

    def get_obj_list(self):
        return []


@cms_resource(resource_name='number')
class MockNumberApi(ApiBase):
    """
    Another mock API, this one has 1000 items and a custom limit, each item
    being a basic MockObject (see class above), that can store just a name
    and id property.

    This is not supposed to be a realistic API, but it implements several
    methods such as hydrate, dehydrate, get_obj, so that API GET, PUT,
    POST can all be tested.
    """

    class Meta:
        limit = 10
        authorization = Authorization()

    def get_obj_list(self):
        return [MockObject({'id': obj_id}) for obj_id in range(1, 1001)]

    def get_obj(self, obj_id):
        return MockObject({'id': obj_id})

    def dehydrate(self, bundle):
        bundle.data = {'id': bundle.obj.id}
        if hasattr(bundle.obj, 'name'):
            bundle.data['name'] = bundle.obj.name
        return bundle

    def hydrate(self, bundle):
        bundle.obj = MockObject(bundle.data)
        return bundle


class ApiBaseTest(TestCase):
    """
    Tests the API base class by registering some actual mock APIs.
    """

    def setUp(self):
        """
        Some of the tests alter properties on the API metaclass, which
        affects other tests after it.

        By creating a backup of these properties before each test in the
        setUp() method, they can be restored after the test in tearDown().
        """
        self.backup_authorization = MockNumberApi._meta.authorization
        self.backup_authentication = MockNumberApi._meta.authentication
        self.backup_paginator = MockNumberApi._meta.paginator_class
        self.backup_always_return_data = MockNumberApi._meta.always_return_data

    def tearDown(self):
        """
        Restore backed up API metaclass properties.
        """
        MockNumberApi._meta.authorization = self.backup_authorization
        MockNumberApi._meta.authentication = self.backup_authentication
        MockNumberApi._meta.paginator_class = self.backup_paginator
        MockNumberApi._meta.always_return_data = self.backup_always_return_data

    @patch('pyramidcms.api.RootFactory')
    def test_get_global_acls(self, mock_root_factory):
        """
        Tests that @cms_resource gets the global list of ACLs from the
        RootFactory class.
        """
        request = testing.DummyRequest()

        # just a simple list will suffice here
        mock_acls = [1, 2, 3]
        mock_root_factory.return_value = Mock(__acl__=mock_acls)
        self.assertListEqual(get_global_acls(request), mock_acls)

    def test_constructor(self):
        """
        Tests that the api_url property is generated properly when creating
        and instance of an API class.
        """
        request = testing.DummyRequest()

        api = MockSimpleApi(request)
        self.assertEqual(api.request, request)
        self.assertEqual(api.api_url, '/api/simple')
        self.assertEqual(api.resource_name, 'simple')
        self.assertEqual(api._meta.limit, 20)

        api = MockNumberApi(request)
        self.assertEqual(api.request, request)
        self.assertEqual(api.api_url, '/api/number')
        self.assertEqual(api.resource_name, 'number')
        self.assertEqual(api._meta.limit, 10)

    def test_paginator_class(self):
        """
        This tests if the correct paginator class from the Meta
        class was used, this can be tested using a MagicMock.
        """
        request = testing.DummyRequest()
        api = MockNumberApi(request)

        mock_paginator = MagicMock()
        api._meta.paginator_class = mock_paginator

        api.paginator.page(1)
        self.assertTrue(mock_paginator.called)

    def test_get_obj_list(self):
        """
        Method should raise NotImplementedError in the ApiBase class.
        """
        request = testing.DummyRequest()

        # create a direct instance of ApiBase (normally you wouldn't do this)
        api = ApiBase(request)
        with self.assertRaises(NotImplementedError):
            api.get_obj_list()

    def test_get_obj(self):
        """
        Method should raise NotImplementedError in the ApiBase class.
        """
        request = testing.DummyRequest()

        # create a direct instance of ApiBase
        api = ApiBase(request)
        with self.assertRaises(NotImplementedError):
            api.get_obj(1)

    def test_delete_obj(self):
        """
        Method should raise NotImplementedError in the ApiBase class.
        """
        request = testing.DummyRequest()
        obj = Mock()

        # create a direct instance of ApiBase
        api = ApiBase(request)
        with self.assertRaises(NotImplementedError):
            api.delete_obj(obj)

    def test_save_obj(self):
        """
        Method should raise NotImplementedError in the ApiBase class.
        """
        request = testing.DummyRequest()
        obj = Mock()

        # create a direct instance of ApiBase
        api = ApiBase(request)
        with self.assertRaises(NotImplementedError):
            api.save_obj(obj)

    def test_build_bundle(self):
        """
        When build_bundle is called without an obj, it should construct
        bundle.obj using the class defined in _meta.object_class.
        """
        # some test data
        request = testing.DummyRequest()
        data = {'id': 1, 'name': 'admin'}

        # back up the current object_class variable, this is needed because
        # the ._meta property is on the ApiBase class, not on the instance.
        backup_object_class = ApiBase._meta.object_class

        # calling build_bundle with an object
        obj = Mock()
        api = ApiBase(request)
        bundle = api.build_bundle(obj=obj, data=data)
        self.assertEqual(bundle.resource, api)
        self.assertEqual(bundle.request, request)
        self.assertEqual(bundle.data, data)
        self.assertEqual(bundle.obj, obj)   # should use obj

        # calling build_bundle without an object
        mock_class = Mock()
        ApiBase._meta.object_class = mock_class
        bundle = api.build_bundle(data=data)
        self.assertEqual(bundle.resource, api)
        self.assertEqual(bundle.request, request)
        self.assertEqual(bundle.data, data)
        self.assertTrue(mock_class.called)  # a new object_class is constructed

        # restore object_class so it doesn't affect other tests.
        ApiBase._meta.object_class = backup_object_class

    def test_hydrate(self):
        """
        Hydrate doesn't really do anything in the ApiBase class,
        it just returns the bundle object as-is.
        """
        request = testing.DummyRequest()
        api = ApiBase(request)

        test_obj = Mock()
        bundle = Bundle(obj=test_obj, request=request)
        hydrated = api.hydrate(bundle)

        # they should be the same objects
        self.assertEqual(bundle, hydrated)

    def test_dehydrate(self):
        """
        Dehydrate doesn't really do anything in the ApiBase class,
        it just returns the original object as-is.
        """
        request = testing.DummyRequest()
        api = ApiBase(request)

        test_obj = Mock()
        bundle = Bundle(obj=test_obj, request=request)
        dehydrated = api.dehydrate(bundle)

        # they should be the same objects
        self.assertEqual(bundle, dehydrated)

    def test_get__success(self):
        """
        Tests the BaseApi.get() method when the object exists.
        """
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}
        api = MockNumberApi(request)

        bundle = api.get()
        self.assertEqual(bundle.data, {'id': 10})

    def test_get__notfound(self):
        """
        Tests the BaseApi.get() method when the object is not found.
        """
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}
        api = MockNumberApi(request)
        api.get_obj = Mock(return_value=None)

        with self.assertRaises(HTTPNotFound):
            api.get()

    def test_get__authorization(self):
        """
        Tests if the BaseApi.get() method has implemented authorization.
        """
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}
        api = MockNumberApi(request)

        auth_mock = Mock()
        api._meta.authorization = auth_mock

        # read_detail can return False for unauthorized
        auth_mock.read_detail.return_value = False
        with self.assertRaisesRegex(HTTPForbidden, NOT_AUTHORIZED):
            api.get()

        # read_detail can also raise HTTPForbidden itself
        # reset return value first...
        auth_mock.read_detail.return_value = Mock()
        auth_mock.read_detail.side_effect = HTTPForbidden

        # don't check the exception message, as we can't set it in a test,
        # if the exception is raised using side_effect.
        with self.assertRaises(HTTPForbidden):
            api.get()

    def test_get__authentication(self):
        """
        Tests if the BaseApi.get() method has implemented authentication.
        """
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}
        api = MockNumberApi(request)

        auth_mock = Mock()
        api._meta.authentication = auth_mock

        # is_authenticated returns False
        auth_mock.is_authenticated.return_value = False
        with self.assertRaisesRegex(HTTPForbidden, NOT_AUTHENTICATED):
            api.get()

        # is_authenticated raises HTTPForbidden
        auth_mock.is_authenticated.return_value = Mock()
        auth_mock.is_authenticated.side_effect = HTTPForbidden

        # don't check the exception message, as we can't set it in a test,
        # if the exception is raised using side_effect.
        with self.assertRaises(HTTPForbidden):
            api.get()

    def test_delete__success(self):
        """
        Tests the success condition of the the BaseApi.delete() method,
        which is the DELETE endpoint for a resource.
        """
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}
        api = MockNumberApi(request)
        delete_mock = Mock()
        api.delete_obj = delete_mock

        response = api.delete()
        self.assertTrue(delete_mock.called)
        self.assertEqual(response.status_code, 204)

    def test_delete__notfound(self):
        """
        When deleting an item that doesnt' exist, the API should
        raise HTTPNotFound.
        """
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}

        api = MockNumberApi(request)
        api.get_obj = Mock(return_value=None)

        with self.assertRaises(HTTPNotFound):
            api.delete()

    def test_delete__authorization(self):
        """
        Tests if the BaseApi.delete() method has implemented authorization.
        """
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}

        api = MockNumberApi(request)
        auth_mock = Mock()
        api._meta.authorization = auth_mock

        # delete_detail can return False for unauthorized
        auth_mock.delete_detail.return_value = False
        with self.assertRaisesRegex(HTTPForbidden, NOT_AUTHORIZED):
            api.delete()

        # delete_detail can also raise HTTPForbidden itself
        # reset return value first...
        auth_mock.delete_detail.return_value = Mock()
        auth_mock.delete_detail.side_effect = HTTPForbidden

        # don't check the exception message, as we can't set it in a test,
        # if the exception is raised using side_effect.
        with self.assertRaises(HTTPForbidden):
            api.delete()

    def test_delete__authentication(self):
        """
        Tests if the BaseApi.delete() method has implemented authentication.
        """
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}
        api = MockNumberApi(request)

        auth_mock = Mock()
        api._meta.authentication = auth_mock

        # is_authenticated returns False
        auth_mock.is_authenticated.return_value = False
        with self.assertRaisesRegex(HTTPForbidden, NOT_AUTHENTICATED):
            api.delete()

        # is_authenticated raises HTTPForbidden
        auth_mock.is_authenticated.return_value = Mock()
        auth_mock.is_authenticated.side_effect = HTTPForbidden

        # don't check the exception message, as we can't set it in a test,
        # if the exception is raised using side_effect.
        with self.assertRaises(HTTPForbidden):
            api.delete()

    def test_put__success(self):
        """
        Tests the success condition of the the BaseApi.put() method,
        which is the PUT endpoint for a resource.
        """
        # some test data to update
        data = {'name': 'admin'}
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}
        request.json_body = data
        request.errors = []

        api = MockNumberApi(request)
        save_mock = Mock()
        api.save_obj = save_mock

        response = api.put()

        self.assertTrue(save_mock.called)
        self.assertEqual(response.status_code, 204)

    def test_put__always_return_data(self):
        """
        Tests that if always_return_data is set on the API Meta class,
        that we get the dehydrated bundle back from the API, rather than
        just a status code of 204.
        """
        # some test data to update
        data = {'name': 'admin'}
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}
        request.json_body = data
        request.errors = []

        api = MockNumberApi(request)
        api._meta.always_return_data = True
        save_mock = Mock()
        api.save_obj = save_mock

        bundle = api.put()

        # return_data is using dehydrate, defined in the NumberApi class.
        self.assertDictEqual(bundle.data, {'id': 10, 'name': 'admin'})
        self.assertTrue(save_mock.called)

    def test_put__invalid_json(self):
        """
        When invalid json data is sent to the API put method, a 400
        bad request should be raised.
        """
        # a property needs to be created on the class, must be cleaned up later
        testing.DummyRequest.json_body = PropertyMock(side_effect=ValueError)
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}

        api = MockNumberApi(request)
        save_mock = Mock()
        api.save_obj = save_mock

        # if request.json_body raises a ValueError, we get a BadRequest
        with self.assertRaises(HTTPBadRequest):
            api.put()

        # must not forget to remove our property for other tests
        delattr(testing.DummyRequest, 'json_body')

    def test_put__validation_errors(self):
        """
        If request.errors contains errors, save_obj() should not be called.
        """
        # some test data to update
        data = {'name': 'admin'}
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}
        request.json_body = data
        request.errors = [{
            'name': 'username',
            'location': 'field',
            'description': 'Username required'
        }]

        api = MockNumberApi(request)
        save_mock = Mock()
        api.save_obj = save_mock

        response = api.put()

        # save should not be called, None is returned
        # because request.errors is set, Cornice will turn this into a 400
        self.assertFalse(save_mock.called)
        self.assertIsNone(response)

    def test_put__notfound(self):
        """
        When updating an item that doesnt' exist, the API should
        raise HTTPNotFound.
        """
        # some test data to update
        data = {'name': 'admin'}
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}
        request.json_body = data
        api = MockNumberApi(request)
        api.get_obj = Mock(return_value=None)

        with self.assertRaises(HTTPNotFound):
            api.put()

    def test_put__authorization(self):
        """
        Tests if the BaseApi.put() method has implemented authorization.
        """
        # some test data to update
        data = {'name': 'admin'}
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}
        request.json_body = data
        api = MockNumberApi(request)

        auth_mock = Mock()
        api._meta.authorization = auth_mock

        # update_detail can return False for unauthorized
        auth_mock.update_detail.return_value = False
        with self.assertRaisesRegex(HTTPForbidden, NOT_AUTHORIZED):
            api.put()

        # update_detail can also raise HTTPForbidden itself
        # reset return value first...
        auth_mock.update_detail.return_value = Mock()
        auth_mock.update_detail.side_effect = HTTPForbidden

        # don't check the exception message, as we can't set it in a test,
        # if the exception is raised using side_effect.
        with self.assertRaises(HTTPForbidden):
            api.put()

    def test_put__authentication(self):
        """
        Tests if the BaseApi.put() method has implemented authentication.
        """
        # some test data to update
        data = {'name': 'admin'}
        request = testing.DummyRequest()
        request.matchdict = {'id': 10}
        request.json_body = data
        api = MockNumberApi(request)

        auth_mock = Mock()
        api._meta.authentication = auth_mock

        # is_authenticated returns False
        auth_mock.is_authenticated.return_value = False
        with self.assertRaisesRegex(HTTPForbidden, NOT_AUTHENTICATED):
            api.put()

        # is_authenticated raises HTTPForbidden
        auth_mock.is_authenticated.return_value = Mock()
        auth_mock.is_authenticated.side_effect = HTTPForbidden

        # don't check the exception message, as we can't set it in a test,
        # if the exception is raised using side_effect.
        with self.assertRaises(HTTPForbidden):
            api.put()

    def test_collection_post__success(self):
        """
        Tests the API collection_post method success condition, which
        should create a new object.
        """
        # test data to create object
        data = {'name': 'admin'}
        request = testing.DummyRequest()
        request.json_body = data
        request.errors = []

        api = MockNumberApi(request)
        save_mock = Mock()
        api.save_obj = save_mock

        response = api.collection_post()

        # save_mock should be called using bundle.obj returned from hydrate
        self.assertTrue(save_mock.called)
        self.assertEqual(response.status_code, 201)

    def test_collection_post__with_id__success(self):
        """
        Tests the API collection_post method also works if we pass an
        id with the data and an object with that id does not exist yet.
        """
        # test data to create object
        data = {'id': 10, 'name': 'admin'}
        request = testing.DummyRequest()
        request.json_body = data
        request.errors = []

        api = MockNumberApi(request)
        save_mock = Mock()
        get_mock = Mock(return_value=None)  # obj with this id does not exist
        api.save_obj = save_mock
        api.get_obj = get_mock

        response = api.collection_post()

        # save_mock should be called using bundle.obj returned from hydrate
        self.assertTrue(save_mock.called)
        self.assertEqual(response.status_code, 201)

    def test_collection_post__with_id__exists(self):
        """
        Tests the API collection_post method will raise a 209 Conflict,
        if the object already exists and we are trying to create an object
        by specifying the id we want.
        """
        # test data to create object
        data = {'id': 10, 'name': 'admin'}
        request = testing.DummyRequest()
        request.json_body = data

        api = MockNumberApi(request)
        save_mock = Mock()
        get_mock = Mock(return_value=MockObject({'id': 10}))  # return same id
        api.save_obj = save_mock
        api.get_obj = get_mock

        with self.assertRaises(HTTPConflict):
            api.collection_post()

    def test_post__always_return_data(self):
        """
        Tests that if always_return_data is set on the API Meta class,
        that we get the dehydrated bundle back from the API, rather than
        just a status code of 201.
        """
        # test data to create object
        data = {'name': 'admin'}
        request = testing.DummyRequest()
        request.json_body = data
        request.errors = []

        api = MockNumberApi(request)
        api._meta.always_return_data = True
        save_mock = Mock()
        api.save_obj = save_mock

        bundle = api.collection_post()

        # return_data is using dehydrate, defined in the NumberApi class.
        self.assertDictEqual(bundle.data, {'id': 10, 'name': 'admin'})
        self.assertTrue(save_mock.called)

    def test_collection_post__invalid_json(self):
        """
        When invalid json data is sent to the API collection_post method, a 400
        bad request should be raised.
        """
        # a property needs to be created on the class, must be cleaned up later
        testing.DummyRequest.json_body = PropertyMock(side_effect=ValueError)
        request = testing.DummyRequest()

        api = MockNumberApi(request)
        save_mock = Mock()
        api.save_obj = save_mock

        # if request.json_body raises a ValueError, we get a BadRequest
        with self.assertRaises(HTTPBadRequest):
            api.collection_post()

        # must not forget to remove our property for other tests
        delattr(testing.DummyRequest, 'json_body')

    def test_collection_post__validation_error(self):
        """
        If request.errors contains errors, save_obj() should not be called.
        """
        # test data to create object
        data = {'name': 'admin'}
        request = testing.DummyRequest()
        request.json_body = data
        request.errors = [{
            'name': 'username',
            'location': 'field',
            'description': 'Username required'
        }]

        api = MockNumberApi(request)
        save_mock = Mock()
        api.save_obj = save_mock

        response = api.collection_post()

        # save should not be called, None is returned
        # because request.errors is set, Cornice will turn this into a 400
        self.assertFalse(save_mock.called)
        self.assertIsNone(response)

    def test_collection_post__authorization(self):
        """
        Tests if the BaseApi.collection_post() method has implemented
        authorization.
        """
        # some test data to update
        data = {'name': 'admin'}
        request = testing.DummyRequest()
        request.json_body = data
        api = MockNumberApi(request)

        auth_mock = Mock()
        api._meta.authorization = auth_mock

        # create_detail can return False for unauthorized
        auth_mock.create_detail.return_value = False
        with self.assertRaisesRegex(HTTPForbidden, NOT_AUTHORIZED):
            api.collection_post()

        # create_detail can also raise HTTPForbidden itself
        # reset return value first...
        auth_mock.create_detail.return_value = Mock()
        auth_mock.create_detail.side_effect = HTTPForbidden

        # don't check the exception message, as we can't set it in a test,
        # if the exception is raised using side_effect.
        with self.assertRaises(HTTPForbidden):
            api.collection_post()

    def test_collection_post__authentication(self):
        """
        Tests if the BaseApi.collection_post() method has implemented
        authentication.
        """
        # some test data to update
        data = {'name': 'admin'}
        request = testing.DummyRequest()
        request.json_body = data
        api = MockNumberApi(request)

        auth_mock = Mock()
        api._meta.authentication = auth_mock

        # is_authenticated returns False
        auth_mock.is_authenticated.return_value = False
        with self.assertRaisesRegex(HTTPForbidden, NOT_AUTHENTICATED):
            api.collection_post()

        # is_authenticated raises HTTPForbidden
        auth_mock.is_authenticated.return_value = Mock()
        auth_mock.is_authenticated.side_effect = HTTPForbidden

        # don't check the exception message, as we can't set it in a test,
        # if the exception is raised using side_effect.
        with self.assertRaises(HTTPForbidden):
            api.collection_post()

    def test_collection_get__success(self):
        """
        Tests the API collection_get method, which returns a list of items.
        """
        # simple api with an empty list
        request = testing.DummyRequest()
        api = MockSimpleApi(request)
        data = api.collection_get()
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
        api = MockNumberApi(request)
        data = api.collection_get()
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
        api = MockNumberApi(request)
        with self.assertRaises(HTTPBadRequest):
            api.collection_get()

    def test_collection_get__authorization(self):
        """
        When collection_get is called, it uses the paginator @reify property
        to get the list of objects to display for the current age.

        The list of objects is filtered based on the authorization class
        that is used, in the paginator @reify property method.

        When this @reify property is called the first time, the filtering
        is applied, so that we create a Paginator object based on the
        filtered results, filtered by the authorization class in use.

        Because the paginator is a @reify property, once it has already been
        called, we have to create a new api object between each test, this is
        normally not a problem on a per-request basis on an api resource when
        the paginator shouldn't change.
        """
        request = testing.DummyRequest()

        # filtered lists can be returned by a more advanced authorization class
        authorized_objects = [MockObject({'id': obj_id}) for obj_id in [10, 5, 2]]
        expected_result = [{'id': 10}, {'id': 5}, {'id': 2}]
        api = MockNumberApi(request)
        auth_mock = MagicMock()
        auth_mock.read_list.return_value = authorized_objects
        api._meta.authorization = auth_mock

        data = api.collection_get()
        self.assertEqual([bundle.data for bundle in data['items']], expected_result)

        # some authorization classes will return an empty list, this is OK
        expected_result = []
        api = MockNumberApi(request)
        auth_mock = MagicMock()
        auth_mock.read_list.return_value = expected_result
        api._meta.authorization = auth_mock

        data = api.collection_get()
        self.assertEqual(data['items'], expected_result)

        # other authorization classes will raise HTTPForbidden
        api = MockNumberApi(request)
        auth_mock = MagicMock()
        auth_mock.read_list.side_effect = HTTPForbidden
        api._meta.authorization = auth_mock

        # don't check the exception message, as we can't set it in a test,
        # if the exception is raised using side_effect.
        with self.assertRaises(HTTPForbidden):
            api.collection_get()

    def test_collection_get__authentication(self):
        """
        Tests the collection_get method when the authentication class
        returns an unauthenticated result, should raise HTTPForbidden.
        """
        request = testing.DummyRequest()
        api = MockNumberApi(request)
        auth_mock = MagicMock()
        api._meta.authentication = auth_mock

        # authentication usually returns False
        auth_mock.is_authenticated.return_value = False
        with self.assertRaisesRegex(HTTPForbidden, NOT_AUTHENTICATED):
            api.collection_get()

        # authentication could also raise HTTPForbidden directly
        auth_mock.is_authenticated.return_value = Mock()
        auth_mock.is_authenticated.side_effect = HTTPForbidden

        # don't check the exception message, as we can't set it in a test
        with self.assertRaises(HTTPForbidden):
            api.collection_get()
