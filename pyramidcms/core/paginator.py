from math import ceil

from sqlalchemy.orm import Query

from pyramidcms.core.exceptions import InvalidPage, PageNotAnInteger


class Paginator(object):

    def __init__(self, items, per_page):
        self.items = items

        # If items is a Query, len() won't work, so use items.count() instead.
        # This will do a COUNT() query, which is fine for most tables, but
        # can get expensive for larger tables, this can be dealt with later.
        if type(items) == Query:
            self.count = items.count()
        else:
            self.count = len(items)

        # If per_page is 0, we create a Paginator over the entire range
        # and set the number of pages to 1. This is used by the API,
        # when setting the limit to 0 it returns all rows.
        self.per_page = int(per_page)
        if self.per_page == 0:
            self.num_pages = 1
        else:
            self.num_pages = int(ceil(self.count / self.per_page))

        self.page_range = range(1, self.num_pages + 1)

    def page(self, page_number):
        return Page(self, page_number)


class Page(object):

    def __init__(self, paginator, number):
        # we only accept integer page numbers
        if type(number) is not int:
            raise PageNotAnInteger('{} is not an integer'.format(number))

        # make sure we get a page in range
        if number < 1 or (number > paginator.num_pages > 1):
            raise InvalidPage('{} is not a valid page number'.format(number))

        self.paginator = paginator
        self.number = number
        self.offset = (self.number - 1) * self.paginator.per_page
        self.object_list = self.paginator.items[self.offset:self.end_index()]

    def has_next(self):
        return self.number < self.paginator.num_pages

    def has_previous(self):
        if self.paginator.per_page == 0:
            return self.offset >= self.paginator.count
        else:
            return self.offset >= self.paginator.per_page

    def has_other_pages(self):
        if self.paginator.per_page == 0:
            return False
        else:
            return self.paginator.count > self.paginator.per_page

    def next_page_offset(self):
        if self.number < self.paginator.num_pages:
            return self.offset + self.paginator.per_page
        else:
            raise InvalidPage('Next page does not exist')

    def previous_page_offset(self):
        if self.number > 1:
            return self.offset - self.paginator.per_page
        else:
            raise InvalidPage('Previous page does not exist')

    def next_page_number(self):
        if self.number < self.paginator.num_pages:
            return self.number + 1
        else:
            raise InvalidPage('Next page does not exist')

    def previous_page_number(self):
        if self.number > 1:
            return self.number - 1
        else:
            raise InvalidPage('Previous page does not exist')

    def start_index(self):
        return self.offset + 1

    def end_index(self):
        if self.paginator.per_page == 0:
            return self.offset + self.paginator.count
        else:
            return self.offset + self.paginator.per_page
