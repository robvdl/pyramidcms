import os
from unittest import TestCase

from pyramidcms import config


class ConfigTests(TestCase):

    def test_resolve_asset_spec(self):
        """
        Test for the :func:`pyramidcms.config.get_asset_spec` function,
        should convert an asset spec to an actual path, but calling it
        again with the path as an argument should do nothing.
        """
        # actual spec gets resolved to a folder
        spec = 'pyramidcms:static'
        folder = config.resolve_asset_spec(spec)
        self.assertTrue(os.path.isdir(folder))
        self.assertNotEqual(spec, folder)

        # resolving the folder again results in no change
        same_folder = config.resolve_asset_spec(folder)
        self.assertEqual(folder, same_folder)
