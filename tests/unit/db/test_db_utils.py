from unittest import TestCase
from unittest.mock import Mock, patch

from pyramidcms import db


class TestDatabaseUtils(TestCase):

    @patch('pyramidcms.db.engine_from_config')
    @patch('pyramidcms.db.DBSession')
    @patch('pyramidcms.db.Base')
    def test_setup_db_connection(self, base_mock, dbsession_mock, engine_from_config_mock):
        """
        Tests the setup_db_connection() function but doesn't need to make
        an actual database connection to do so.
        """
        # we don't actually create or open this db during the test
        fake_db = 'sqlite:////tmp/test.db'
        settings = {'sqlalchemy.url': fake_db}
        engine_mock = Mock()
        engine_from_config_mock.return_value = engine_mock

        # run the method under test
        db.setup_db_connection(settings)

        engine_from_config_mock.assert_called_once_with(settings, 'sqlalchemy.')
        dbsession_mock.configure.assert_called_once_with(bind=engine_mock)
        self.assertEqual(base_mock.metadata.bind, engine_mock)
