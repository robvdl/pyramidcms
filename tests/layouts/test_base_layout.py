from unittest import TestCase
from unittest.mock import Mock

from pyramid import testing

from pyramidcms.layouts.base import BaseLayout


class BaseLayoutTests(TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()

    def test_logged_in(self):
        """
        Tests the view.logged_in reify property, note that this uses the
        request.user property, which is a lazy loaded property on the
        request object.

        However we are not testing this lazy loaded property on the request
        object, so replace this with a mock.
        """
        self.request.user = None
        layout = BaseLayout(self.request)
        self.assertFalse(layout.logged_in)

        self.request.user = Mock()
        layout = BaseLayout(self.request)
        self.assertTrue(layout.logged_in)

    def test_csrf_token(self):
        """
        Just a simple test to ensure the view.csrf_token reify property
        returns the CSRF token, which is always the same when using
        pyramid.testing.DummyRequest.
        """
        layout = BaseLayout(self.request)
        self.assertEqual(layout.csrf_token, '0123456789012345678901234567890123456789')
