from unittest import TestCase
from unittest.mock import Mock

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound
from cornice.resource import resource

from pyramidcms.api import ModelApi


@resource(collection_path='/api/model', path='/api/model/{id}')
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
        Test that ModelApi.get_obj(obj_id) raises a HTTPNotFound if
        the database record with that id does not exist.
        """
        request = testing.DummyRequest()
        resource1 = MockModelApi(request)
        resource1._meta.model.objects.get.return_value = None

        with self.assertRaises(HTTPNotFound):
            resource1.get_obj(10)

    def test_dehydrate(self):
        """
        Checks that the dehydrate method calls model.serialize()
        """
        request = testing.DummyRequest()
        resource1 = MockModelApi(request)

        mock_model_instance = Mock()
        resource1.dehydrate(mock_model_instance)

        # check if mock_model_instance.serialize() was called
        mock_model_instance.serialize.assert_called_with()
