from unittest import TestCase
from unittest.mock import Mock, patch

from pyramid import testing

from pyramidcms.views.auth import AuthViews


class TestLoginView(TestCase):

    def test_login_form(self):
        form_instance_mock = Mock()
        form_class_mock = Mock(return_value=form_instance_mock)
        request = testing.DummyRequest()
        view = AuthViews(request)

        with patch('pyramidcms.views.auth.LoginForm', form_class_mock):
            result = view.login()

        self.assertDictEqual(result, {
            'return_url': request.url,
            'form': form_instance_mock
        })        



    def test_disabled_user_login_fails(self):
        pass

    def test_user_login(self):
        pass

    def test_superuser_login(self):
        pass


class TestLogoutView(TestCase):
    pass
