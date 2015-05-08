from unittest import TestCase
from unittest.mock import Mock, patch

from pyramidcms import db


class ModelManagerTests(TestCase):

    def setUp(self):
        self.manager = db.ModelManager()
        self.manager.model = Mock()

    @patch('pyramidcms.db.DBSession')
    def test_all(self, mock_session):
        """
        A really basic test that checks if the ModelManager.all() method
        executes the query DBSession.query(model) which simply returns
        all rows for that model.
        """
        self.manager.all()
        mock_session.query.assert_called_once_with(self.manager.model)

    @patch('pyramidcms.db.DBSession', Mock())
    def test_create(self):
        """
        This tests the ModelManager.create() method, it checks two things
        using mocks:

        First, it checks that an instance of the model is created and
        both *args and **kwargs are passed to the model.

        Secondly, it checks that save() is called on the model instance.
        """
        args = [1, 2, 3]
        kwargs = {'a': True, 'b': False}
        mock_obj = Mock()
        self.manager.model.return_value = mock_obj

        self.manager.create(*args, **kwargs)
        self.manager.model.assert_called_once_with(*args, **kwargs)
        self.assertTrue(mock_obj.save.called)

    @patch('pyramidcms.db.DBSession')
    def test_filter(self, mock_session):
        """
        This tests the ModelManager.filter() method, it checks that
        the equivalent SQLAlchemy query is executed::

            DBSession.query(model).filter_by(**kwargs)

        It checks that the arguments **kwargs to the ModelManager.filter()
        method are passed to the filter_by() method on the queryset.
        """
        kwargs = {'a': True, 'b': False}
        mock_query = Mock()
        mock_session.query.return_value = mock_query

        self.manager.filter(**kwargs)

        mock_session.query.assert_called_once_with(self.manager.model)
        mock_query.filter_by.assert_called_once_with(**kwargs)

    def test_get(self):
        """
        Test the ModelManager.get() method, this checks that the
        equivalent SQLAlchemy query is executed::

            DBSession.query(model).filter_by(**kwargs).first()

        We don't need to patch DBSession here, because we know that
        the ModelManager.get() method actually calls ModelManager.filter()
        first, so we just mock that out instead.
        """
        kwargs = {'a': True, 'b': False}
        mock_query = Mock()

        # mock out the filter method, we are already testing it elsewhere
        self.manager.filter = Mock(return_value=mock_query)

        # calling .get() calls our mock .filter() method which then returns
        # the mock_query object, we simply check if .first() was called on
        # this mock_query object, the rest is already tested elsewhere.
        self.manager.get(**kwargs)
        self.assertTrue(mock_query.first.called)

    @patch('pyramidcms.db.DBSession')
    def test_count(self, mock_session):
        """
        A simple test for ModelManager.count() which should generate
        the following SQLAlchemy query::

            DBSession.query(model).count()

        This would normally the number of rows for this model, it is
        tested using mock.
        """
        mock_query = Mock()
        mock_session.query.return_value = mock_query

        self.manager.count()
        mock_session.query.assert_called_once_with(self.manager.model)
        self.assertTrue(mock_query.count.called)
