from unittest import TestCase
from unittest.mock import Mock

from pyramidcms.api import Bundle


class BundleTests(TestCase):
    """
    Tests for the api Bundle object.
    """

    def test_repr(self):
        """
        The only thing we can really test here is the __repr__ method.
        """
        # no data or obj
        bundle = Bundle(obj=None, data=None)
        self.assertEqual(repr(bundle),
                         "<Bundle for obj: 'None' and with data: {}>")

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
