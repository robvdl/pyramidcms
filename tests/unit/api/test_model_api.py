from unittest import TestCase
from unittest.mock import Mock

from pyramid import testing

from pyramidcms.api import ModelApi, Bundle, cms_resource


@cms_resource(resource_name='model')
class MockModelApi(ModelApi):
    """
    A mock ModelApi that uses a Mock rather than an actual model.
    """

    class Meta:
        # usually the model is a class rather than instance,
        # but this should do fine for testing.
        model = Mock()


class ModelApiTests(TestCase):

    def test_get_obj_list(self):
        """
        Test that ModelApi.get_obj_list() runs the query: model.objects.all()
        """
        request = testing.DummyRequest()
        api = MockModelApi(request)
        api.get_obj_list()

        # check if _meta.model.objects.all() was called
        api._meta.model.objects.all.assert_called_with()

    def test_get_obj__success(self):
        """
        Test that ModelApi.get_obj(obj_id) runs the correct query.
        """
        request = testing.DummyRequest()
        api = MockModelApi(request)
        api._meta.model.objects.get.return_value = Mock()

        api.get_obj(10)

        api._meta.model.objects.get.assert_called_with(id=10)

    def test_get_obj__notfound(self):
        """
        Test that ModelApi.get_obj(obj_id), should just return None
        if the object does not exist, will raise HTTPNotFound in
        the BaseApi class get() method instead.
        """
        request = testing.DummyRequest()
        api = MockModelApi(request)
        api._meta.model.objects.get.return_value = None

        self.assertIsNone(api.get_obj(10))

    def test_delete_obj(self):
        """
        The delete_obj method should just call .delete() on the object.
        """
        request = testing.DummyRequest()
        api = MockModelApi(request)
        obj = Mock()

        api.delete_obj(obj)

        obj.delete.assert_called_with()

    def test_save_obj(self):
        """
        The save_obj method should just call .save(flush=True) on the object.
        """
        request = testing.DummyRequest()
        api = MockModelApi(request)
        obj = Mock()

        api.save_obj(obj)

        obj.save.assert_called_with(flush=True)

    def test_dehydrate(self):
        """
        Checks that the dehydrate method calls model.serialize()
        """
        request = testing.DummyRequest()
        api = MockModelApi(request)

        obj = Mock()
        bundle = Bundle(obj=obj, resource=api, request=request)
        api.dehydrate(bundle)

        # check if mock_model_instance.serialize() was called
        obj.serialize.assert_called_with()

    def test_hydrate(self):
        """
        Checks that the hydrate method calls model.deserialize()
        """
        request = testing.DummyRequest()
        api = MockModelApi(request)

        obj = Mock()
        data = {'id': 10, 'name': 'admin'}
        bundle = Bundle(obj=obj, data=data, resource=api, request=request)
        api.hydrate(bundle)

        # check if mock_model_instance.serialize() was called
        obj.deserialize.assert_called_with(data)
