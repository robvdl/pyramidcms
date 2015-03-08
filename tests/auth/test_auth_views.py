from unittest import TestCase
from unittest.mock import Mock, patch

from pyramid import testing

from pyramidcms.views.auth import AuthViews
from pyramidcms.forms.auth import LoginForm


class TestLoginView(TestCase):

    def test_login_form(self):
        form_instance_mock = Mock()
        request = testing.DummyRequest()
        view = AuthViews(request)

        with patch('pyramidcms.forms.auth.LoginForm', 
                   Mock(return_value=form_instance_mock)):
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
