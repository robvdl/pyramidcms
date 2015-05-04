from unittest import TestCase

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from pyramidcms.views.static import static_view
from pyramidcms.config import get_static_dirs


class TestStaticView(TestCase):
    """
    Tests the static view, used in development mode.

    This view should serve static files from any of the folders listed in the
    static.dirs setting of the pyramid .ini file.

    Any asset specs used in static.dirs are converted to full paths when the
    application starts up, so that the view can assume regular paths only.
    """

    def test_static_view__disabled(self):
        request = testing.DummyRequest()
        request.matchdict['subpath'] = ('.gitkeep',)  # a file that exists

        settings = {
            'static.serve': False,   # must be False for this test
            'static.dirs': 'pyramidcms:static'
        }
        settings['static.dirs'] = get_static_dirs(settings)
        request.registry.settings = settings

        # we can only really test for a 404 if static.serve is False.
        with self.assertRaises(HTTPNotFound):
            static_view(request)

    def test_static_view__success(self):
        request = testing.DummyRequest()
        request.matchdict['subpath'] = ('.gitkeep',)  # a file that exists

        settings = {
            'static.serve': True,
            'static.dirs': 'pyramidcms:static'
        }
        settings['static.dirs'] = get_static_dirs(settings)
        request.registry.settings = settings

        # the file exists, should not raise a 404
        static_view(request)

    def test_static_view__notfound(self):
        request = testing.DummyRequest()
        request.matchdict['subpath'] = ('foo',)  # a file that doesn't exist

        settings = {
            'static.serve': True,
            'static.dirs': 'pyramidcms:static'
        }
        settings['static.dirs'] = get_static_dirs(settings)
        request.registry.settings = settings

        # the file doesn't exist, should raise a 404
        with self.assertRaises(HTTPNotFound):
            static_view(request)
