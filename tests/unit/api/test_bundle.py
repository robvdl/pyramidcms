from unittest import TestCase
from unittest.mock import Mock

from pyramid import testing

from pyramidcms.api import Bundle


class BundleTests(TestCase):
    """
    Tests for the api Bundle object.
    """

    def test_repr(self):
        """
        The only thing we can really test here is the __repr__ method.
        """
        # no obj is used in API lists
        bundle = Bundle(obj=None, data=None)
        self.assertEqual(repr(bundle), '<Bundle with items: []>')

        # using a mock obj with an __str__ method.
        obj = Mock()
        obj.__str__ = Mock(return_value='test_str')
        bundle = Bundle(obj=obj, data=None)
        self.assertEqual(repr(bundle),
                         "<Bundle for obj: 'test_str' and with data: {}>")

        # add some data
        data = {'id': 10}
        bundle = Bundle(obj=obj, data=data)
        self.assertEqual(repr(bundle),
                         "<Bundle for obj: 'test_str' and with data: {'id': 10}>")

    def test_json(self):
        """
        There should be a __json__ method on the bundle, that either returns
        bundle.data for single object bundles, or serializes list API bundles.
        """
        # single object bundle
        request = testing.DummyRequest()
        data = {'id': 10}
        bundle = Bundle(obj=Mock(), data=data)
        self.assertDictEqual(bundle.__json__(request), bundle.data)

        # list of objects, each item must be a Bundle too
        items = [Bundle(obj=Mock(), data={'number': n}) for n in range(1, 11)]
        meta = {'meta': 'data'}
        bundle = Bundle(meta=meta, items=items)
        self.assertDictEqual(bundle.__json__(request), {
            'items': [
                {'number': 1},
                {'number': 2},
                {'number': 3},
                {'number': 4},
                {'number': 5},
                {'number': 6},
                {'number': 7},
                {'number': 8},
                {'number': 9},
                {'number': 10}
            ],
            'meta': {'meta': 'data'}
        })
