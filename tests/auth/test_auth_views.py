from unittest import TestCase
from unittest.mock import Mock, patch

from pyramid import testing
from webob.multidict import MultiDict

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
        # create a mock POST request
        request = testing.DummyRequest(post={'username': 'dummy', 'password': '123'})
        request.POST = MultiDict(request.POST)
        view = AuthViews(request)

        # mock the User model and instance
        user_instance_mock = Mock()
        user_instance_mock.check_password.return_value = True
        user_instance_mock.active = False
        user_model_mock = Mock()
        user_model_mock.objects.get.return_value = user_instance_mock

        # patch the session.flash message and use it as a means of testing
        request.session.flash = Mock()

        with patch('pyramidcms.views.auth.User', user_model_mock):
            view.login()

        # we can test for a specific flash message
        request.session.flash.assert_called_once_with('User account is disabled', queue='error')

    def test_invalid_credentials_fails(self):
        pass

    def test_user_login(self):
        pass

    def test_superuser_login(self):
        pass


class TestLogoutView(TestCase):
    pass
