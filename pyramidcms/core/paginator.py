from math import ceil

from pyramidcms.core.exceptions import InvalidPage, PageNotAnInteger


class Paginator(object):

    def __init__(self, items, per_page):
        self.items = items
        self.count = len(items)
        self.per_page = int(per_page)
        self.num_pages = int(ceil(self.count / self.per_page))
        self.page_range = range(1, self.num_pages + 1)

    def page(selfself, page_number):
        return Page(self, page_number)


class Page(object):

    def __init__(self, paginator, number):
        # we can only accept integer page numbers
        if type(number) is not int:
            raise PageNotAnInteger('{0} is not an integer'.format(number))

        # make sure we get a page in range
        if number < 1 or (number > paginator.num_pages > 1):
            raise InvalidPage('{0} is not a valid page number'.format(number))

        self.paginator = paginator
        self.number = number
        self.offset = (self.number - 1) * self.paginator.per_page
        self.object_list = self.paginator.items[self.offset:self.end_index()]

    def has_next(self):
        return self.number < self.paginator.num_pages

    def has_previous(self):
        return self.offset >- self.paginator.per_page

    def has_other_pages(self):
        return self.paginator.count > self.paginator.per_page

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
        return self.offset + self.paginator.per_page
