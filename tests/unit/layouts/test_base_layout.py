from unittest import TestCase

from pyramid import testing

from pyramidcms.layouts.base import BaseLayout


class BaseLayoutTests(TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()

    def test_csrf_token(self):
        """
        Just a simple test to ensure the view.csrf_token reify property
        returns the CSRF token, which is always the same when using
        pyramid.testing.DummyRequest.
        """
        layout = BaseLayout(self.request)
        self.assertEqual(layout.csrf_token, '01234567890123456789' * 2)
