import unittest

from pyramidcms.core.paginator import Paginator, Page
from pyramidcms.core.exceptions import InvalidPage, PageNotAnInteger


class PaginationTest(unittest.TestCase):
    """
    Tests for the Paginator and Page classes.
    """

    def test_paginator_constructor(self):
        """
        Tests the Paginator constructor.
        """
        paginator = Paginator(range(1000), 50)
        self.assertEqual(paginator.count, 1000)
        self.assertEqual(paginator.per_page, 50)
        self.assertEqual(paginator.num_pages, 20)
        self.assertEqual(paginator.page_range, range(1, 21))

        paginator = Paginator(range(997), 43)
        self.assertEqual(paginator.count, 997)
        self.assertEqual(paginator.per_page, 43)
        self.assertEqual(paginator.num_pages, 24)
        self.assertEqual(paginator.page_range, range(1, 25))

    def test_paginator_page(self):
        """
        Tests for the paginator.page() method, which returns a Page object.

        This also tests the Page class constructor.
        """
        paginator = Paginator(range(1000), 50)

        page = paginator.page(1)
        self.assertEqual(type(page), Page)
        self.assertEqual(type(page.paginator), Paginator)
        self.assertEqual(page.number, 1)
        self.assertEqual(page.offset, 0)

        page = paginator.page(12)
        self.assertEqual(page.number, 12)
        self.assertEqual(page.offset, 550)

        page = paginator.page(20)
        self.assertEqual(page.number, 20)
        self.assertEqual(page.offset, 950)

        with self.assertRaises(InvalidPage):
            paginator.page(21)

        with self.assertRaises(InvalidPage):
            paginator.page(0)

        with self.assertRaises(PageNotAnInteger):
            paginator.page(1.5)

        # special case: if 0 items in paginator, page 1 should still work
        paginator = Paginator([], 10)
        page = paginator.page(1)
        self.assertEqual(page.number, 1)
        self.assertEqual(page.offset, 0)

    def test_page_has_next(self):
        """
        Tests the page.has_next() method.
        """
        paginator = Paginator(range(1000), 50)

        page = paginator.page(1)
        self.assertTrue(page.has_next())

        page = paginator.page(10)
        self.assertTrue(page.has_next())

        page = paginator.page(20)
        self.assertFalse(page.has_next())

    def test_page_has_previous(self):
        """
        Tests the page.has_previous() method.
        """
        paginator = Paginator(range(1000), 50)

        page = paginator.page(1)
        self.assertFalse(page.has_previous())

        page = paginator.page(10)
        self.assertTrue(page.has_previous())

        page = paginator.page(20)
        self.assertTrue(page.has_previous())

    def test_page_has_other_pages(self):
        """
        Tests the page.has_other_pages() method.
        """
        paginator = Paginator(range(100), 50)

        page = paginator.page(1)
        self.assertTrue(page.has_other_pages())

        page = paginator.page(2)
        self.assertTrue(page.has_other_pages())

        paginator = Paginator(range(50), 50)

        page = paginator.page(1)
        self.assertFalse(page.has_other_pages())

    def test_next_page_offset(self):
        """
        Tests the page.next_page_offset() method.
        """
        paginator = Paginator(range(1000), 50)

        page = paginator.page(1)
        self.assertEqual(page.next_page_offset(), 50)

        page = paginator.page(2)
        self.assertEqual(page.next_page_offset(), 100)

        page = paginator.page(19)
        self.assertEqual(page.next_page_offset(), 950)

        page = paginator.page(20)
        with self.assertRaises(InvalidPage):
            page.next_page_offset()

    def test_previous_page_offset(self):
        """
        Tests the page.previous_page_offset() method.
        """
        paginator = Paginator(range(1000), 50)

        page = paginator.page(2)
        self.assertEqual(page.previous_page_offset(), 0)

        page = paginator.page(20)
        self.assertEqual(page.previous_page_offset(), 900)

        page = paginator.page(1)
        with self.assertRaises(InvalidPage):
            page.previous_page_offset()

    def test_next_page_number(self):
        """
        Tests the page.next_page_number() method.
        """
        paginator = Paginator(range(1000), 50)

        page = paginator.page(1)
        self.assertEqual(page.next_page_number(), 2)

        page = paginator.page(2)
        self.assertEqual(page.next_page_number(), 3)

        page = paginator.page(19)
        self.assertEqual(page.next_page_number(), 20)

        page = paginator.page(20)
        with self.assertRaises(InvalidPage):
            page.next_page_number()

    def test_previous_page_number(self):
        """
        Tests the page.previous_page_number() method.
        """
        paginator = Paginator(range(1000), 50)

        page = paginator.page(2)
        self.assertEqual(page.previous_page_number(), 1)

        page = paginator.page(20)
        self.assertEqual(page.previous_page_number(), 19)

        page = paginator.page(1)
        with self.assertRaises(InvalidPage):
            page.previous_page_number()

    def test_start_end_index(self):
        """
        Tests the page.start_index() and page.end_index() methods.
        """
        paginator = Paginator(range(1000), 50)

        page = paginator.page(1)
        self.assertEqual(page.start_index(), 1)
        self.assertEqual(page.end_index(), 50)

        page = paginator.page(3)
        self.assertEqual(page.start_index(), 101)
        self.assertEqual(page.end_index(), 150)

        page = paginator.page(20)
        self.assertEqual(page.start_index(), 951)
        self.assertEqual(page.end_index(), 1000)
