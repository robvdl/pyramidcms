from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import InstrumentedList

from pyramidcms import db


# These mock models are used for testing

class UserModel(db.Model):
    username = Column(String)
    fullname = Column(String)
    password = Column(String)


class ApiModel(db.Model):
    token = Column(String(50), unique=True)
    user_id = Column(Integer, ForeignKey('user_model.id'))
    description = Column(String(30))
    user = relationship('UserModel')


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
        class DBModelWithLongName(db.BaseModel):
            pass

        model = db.BaseModel()
        self.assertEqual(model.__tablename__, 'base_model')

        model = DBModelWithLongName()
        self.assertEqual(model.__tablename__, 'db_model_with_long_name')

    @patch('pyramidcms.db.ModelManager', Mock())
    def test_repr(self):
        """
        The repr() method on a model generates a string based on the
        model class name and calling str() on the model.
        """
        class MockModel(db.BaseModel):
            def __str__(self):
                return 'str_method'

        model = MockModel()
        self.assertEqual(repr(model), '<MockModel: str_method>')

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

    @patch('pyramidcms.db.ModelManager', Mock())
    @patch('pyramidcms.db.DBSession')
    @patch('pyramidcms.db.transaction')
    def test_commit_manually(self, mock_transaction, mock_session):
        """
        The save method should commit manually if the optional commit
        argument is True.
        """
        model = db.BaseModel()
        model.save(True)
        mock_session.add.assert_called_once_with(model)

        # transaction.commit() should have been called
        mock_transaction.commit.assert_called_once_with()

    @patch('pyramidcms.db.ModelManager', Mock())
    def test_serialize(self):
        """
        Unit test for the serialize() method on models, done using mocks.

        Tests done using full=False and full=True parameter, also tests
        different field types, e.g. int, datetime, foreign key and m2m.
        """
        class MockModel(db.BaseModel):
            orm_fields = ['fk_field', 'm2m_field', 'int_field', 'str_field',
                          'bool_field', 'null_field', 'date_field']
            fk_field = Mock(spec=db.Model, id=1, serialize=Mock(return_value={'id': 1}))
            m2m_field = InstrumentedList([Mock(id=2, serialize=Mock(return_value={'id': 2}))])
            int_field = 10
            str_field = 'string field'
            bool_field = True
            null_field = None
            date_field = datetime.now()
            not_a_field = 'not a field'

        model = MockModel()

        self.assertDictEqual(model.serialize(), {
            'bool_field': True,
            'int_field': 10,
            'date_field': model.date_field.isoformat(),
            'fk_field': 1,
            'm2m_field': [2],
            'str_field': 'string field',
            'null_field': None
        })

        self.assertDictEqual(model.serialize(full=True), {
            'bool_field': True,
            'int_field': 10,
            'date_field': model.date_field.isoformat(),
            'fk_field': {'id': 1},
            'm2m_field': [{'id': 2}],
            'str_field': 'string field',
            'null_field': None
        })

    @patch('pyramidcms.db.ModelManager', Mock())
    def test_orm_fields(self):
        """
        Test the model.orm_fields property, requires an actual model to test.
        """
        model = ApiModel()

        # orm_fields should include user but not user_id
        self.assertListEqual(sorted(model.orm_fields), ['description', 'id', 'token', 'user'])

    @patch('pyramidcms.db.ModelManager', Mock())
    def test_db_columns(self):
        """
        Test the model.db_columns property, requires an actual model to test.
        """
        model = ApiModel()

        # db_columns should include user_id but not user
        self.assertListEqual(sorted(model.db_columns), ['description', 'id', 'token', 'user_id', ])
