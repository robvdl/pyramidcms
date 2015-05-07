import os
from unittest import TestCase

from pyramid.config import Configurator

from pyramidcms.config import setup_configurator, resolve_asset_spec


class ConfigTests(TestCase):

    def test_setup_configurator(self):
        """
        A simple test for the :func:`pyramidcms.config.setup_configurator`
        function, given some test settings, ensures we get a Configurator
        object back.
        """
        settings = {
            'session.secret': 'super-secret-key',
            'session.cookie_httponly': True,
            'session.cookie_secure': False,
        }

        config = setup_configurator(settings)
        self.assertEqual(type(config), Configurator)

    def test_resolve_asset_spec(self):
        """
        Test for the :func:`pyramidcms.config.get_asset_spec` function,
        should convert an asset spec to an actual path, but calling it
        again with the path as an argument should do nothing.
        """
        # actual spec gets resolved to a folder
        spec = 'pyramidcms:static'
        folder = resolve_asset_spec(spec)
        self.assertTrue(os.path.isdir(folder))
        self.assertNotEqual(spec, folder)

        # resolving the folder again results in no change
        same_folder = resolve_asset_spec(folder)
        self.assertEqual(folder, same_folder)
