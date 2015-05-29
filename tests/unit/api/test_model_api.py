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
        resource1 = MockModelApi(request)
        resource1.get_obj_list()

        # check if _meta.model.objects.all() was called
        resource1._meta.model.objects.all.assert_called_with()

    def test_get_obj__success(self):
        """
        Test that ModelApi.get_obj(obj_id) runs the correct query.
        """
        request = testing.DummyRequest()
        resource1 = MockModelApi(request)
        resource1._meta.model.objects.get.return_value = Mock()

        resource1.get_obj(10)

        resource1._meta.model.objects.get.assert_called_with(id=10)

    def test_get_obj__notfound(self):
        """
        Test that ModelApi.get_obj(obj_id), should just return None
        if the object does not exist, will raise HTTPNotFound in
        the BaseApi class get() method instead.
        """
        request = testing.DummyRequest()
        resource1 = MockModelApi(request)
        resource1._meta.model.objects.get.return_value = None

        self.assertIsNone(resource1.get_obj(10))

    def test_dehydrate(self):
        """
        Checks that the dehydrate method calls model.serialize()
        """
        request = testing.DummyRequest()
        resource1 = MockModelApi(request)

        mock_model_instance = Mock()
        bundle = Bundle(obj=mock_model_instance, request=request)
        resource1.dehydrate(bundle)

        # check if mock_model_instance.serialize() was called
        mock_model_instance.serialize.assert_called_with()
