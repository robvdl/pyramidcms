from unittest import TestCase
from unittest.mock import Mock, patch

from pyramidcms import db


class BaseModelTests(TestCase):

    @patch('pyramidcms.db.ModelManager')
    def test_objects(self, mock_manager):
        """
        The Model.objects property (which is a @declared_attr) should
        return an instance of it's manager class.
        """
        mock_manager_instance = Mock()
        mock_manager.return_value = mock_manager_instance
        model = db.BaseModel()
        self.assertEqual(model.objects, mock_manager_instance)

    @patch('pyramidcms.db.ModelManager', Mock())
    def test_tablename(self):
        """
        Tests the Model.__tablename__ property (which is a @declared_attr).

        The tablename should be generated from the name of the model class,
        but using lowercase and underscores instead of camel case.
        """
        model = db.BaseModel()
        self.assertEqual(model.__tablename__, 'base_model')

        class ModelWithLongName(db.BaseModel):
            pass

        model = ModelWithLongName()
        self.assertEqual(model.__tablename__, 'model_with_long_name')

    @patch('pyramidcms.db.ModelManager', Mock())
    def test_repr(self):
        """
        The repr() method on a model generates a string based on the
        model class name and calling str() on the model.
        """
        class CustomModel(db.BaseModel):
            def __str__(self):
                return 'str_method'

        model = CustomModel()
        self.assertEqual(repr(model), '<CustomModel: str_method>')

    @patch('pyramidcms.db.ModelManager', Mock())
    def test_delete(self):
        """
        Test the delete() method on the model instance, should call .filter()
        on the model manager instance which returns a queryset, it should then
        call the .delete() method on that queryset.
        """
        model = db.BaseModel()
        queryset_mock = Mock()
        model.objects.filter.return_value = queryset_mock

        model.delete()

        model.objects.filter.assert_called_once_with(id=model.id)
        self.assertTrue(queryset_mock.delete.called)

    @patch('pyramidcms.db.ModelManager', Mock())
    @patch('pyramidcms.db.DBSession')
    def test_save(self, mock_session):
        """
        The save method should add the model instance to the SQLAlchemy
        session object.
        """
        model = db.BaseModel()
        model.save()
        mock_session.add.assert_called_once_with(model)
