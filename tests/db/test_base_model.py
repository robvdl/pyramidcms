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

    def test_repr(self):
        """
        The repr() method on a model generates a string based on the
        model class name and calling str() on the model.

        :return:
        """
        db.BaseModel.__str__ = Mock(return_value='str_return_value')

        model = db.BaseModel()
        self.assertEqual(repr(model), '<BaseModel: str_return_value>')

        class CustomModel(db.BaseModel):
            pass

        model = CustomModel()
        self.assertEqual(repr(model), '<CustomModel: str_return_value>')
