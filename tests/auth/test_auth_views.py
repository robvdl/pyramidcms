from unittest import TestCase
from unittest.mock import Mock

from pyramid import testing

from pyramidcms.views.auth import AuthViews


class TestLoginView(TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.auth = AuthViews(self.request)

    def tearDown(self):
        pass

    def test_empty_login_fails(self):
        result = self.auth.login()
        self.assertEqual(result.status, '403')

    def test_disabled_user_login_fails(self):
        pass

    def test_user_login(self):
        pass

    def test_superuser_login(self):
        pass


class TestLogoutView(TestCase):
    pass
