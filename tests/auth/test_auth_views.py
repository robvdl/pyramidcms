from unittest import TestCase
from unittest.mock import Mock, patch

from pyramid import testing
from webob.multidict import MultiDict

from pyramidcms.views.auth import AuthViews


class TestLoginView(TestCase):
    """
    Tests for :class:`pyramidcms.views.auth.AuthViews` class.
    """

    def test_login_form(self):
        """
        This test checks that we can retrieve the login form.
        """
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
        """
        This test checks that a user with the correct username and password but
        with a disabled or invalid account fails to login.
        """
        # create a mock POST request
        request = testing.DummyRequest(post={'username': 'dummy', 'password': '123'})
        request.POST = MultiDict(request.POST)
        view = AuthViews(request)

        # mock the User model and instance
        user_instance_mock = Mock()
        user_instance_mock.check_password.return_value = True
        user_instance_mock.is_active = False
        user_model_mock = Mock()
        user_model_mock.objects.get.return_value = user_instance_mock

        # patch the session.flash message and use it as a means of testing
        request.session.flash = Mock()

        with patch('pyramidcms.views.auth.User', user_model_mock):
            view.login()

        # we can test for a specific flash message
        request.session.flash.assert_called_once_with('User account is disabled', queue='error')

    def test_invalid_credentials_fails(self):
        """
        This test checks that a user with the wrong password cannot login.
        """
        # create a mock POST request
        request = testing.DummyRequest(post={'username': 'dummy', 'password': '123'})
        request.POST = MultiDict(request.POST)
        view = AuthViews(request)

        # mock the User model and instance
        user_instance_mock = Mock()
        user_instance_mock.check_password.return_value = False
        user_model_mock = Mock()
        user_model_mock.objects.get.return_value = user_instance_mock

        # patch the session.flash message and use it as a means of testing
        request.session.flash = Mock()

        with patch('pyramidcms.views.auth.User', user_model_mock):
            view.login()

        # we can test for a specific flash message
        request.session.flash.assert_called_once_with('Invalid username or password', queue='error')

    def test_valid_user_login(self):
        # create a mock POST request
        request = testing.DummyRequest(post={'username': 'dummy', 'password': '123'})
        request.POST = MultiDict(request.POST)
        view = AuthViews(request)

        # mock the User model and instance
        user_instance_mock = Mock()
        user_instance_mock.check_password.return_value = True
        user_model_mock = Mock()
        user_model_mock.objects.get.return_value = user_instance_mock

        # patch the session.flash message and use it as a means of testing
        request.session.flash = Mock()

        with patch('pyramidcms.views.auth.User', user_model_mock):
            view.login()

        # we can test for a specific flash message
        request.session.flash.assert_called_once_with('You are logged in', queue='success')
