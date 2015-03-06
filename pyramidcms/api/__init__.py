from pyramid.httpexceptions import HTTPBadRequest

from pyramidcms.core.paginator import Paginator


class ApiBase(object):
    """
    The ApiBase class is for building RESTful resources built on top of
    Mozilla Cornice. Originally the design was modelled a bit after TastyPie,
    a RESTful API library for Django.

    There are some slight differences however, for a start we don't call the
    base class a Resource, mainly because Pyramid already has something
    called a Resource which has a completely different meaning and would
    therefore confuse Pyramid developers.

    Also, TastyPie uses offset/limit, while we use page/limit instead.
    Having offset/limit allows the front end to retrieve data starting in
    the middle of a page, however this just made the Paginator and Page
    classes more complex and just wasn't that useful, so page was used
    instead of offset.
    """
    _services = None

    class Meta:
        limit = 20

    def __init__(self, request):
        self.request = request
        self._meta = self.Meta()
        self.api_url = self._get_api_url()

    def _get_api_url(self):
        key = [s for s in self._services if s.startswith('collection_')][0]
        return self._services[key].path

    def obj_list(self):
        """
        The obj_list method must be implemented by the derived API
        class, the stub here just returns an empty list.
        """
        return []

    def collection_get(self):
        """
        The API collection_get method is used by Cornice, it returns a list
        of items for this API class.
        """
        paginator = Paginator(self.obj_list(), self._meta.limit)
        try:
            page_number = int(self.request.GET.get('page', 1))
            page = paginator.page(page_number)
        except ValueError:
            raise HTTPBadRequest('Invalid page number')

        if page.has_next():
            next_page = page.next_page_number()
            next_page_url = '{}?page={}'.format(self.api_url, next_page)
        else:
            next_page_url = None

        if page.has_previous():
            prev_page = page.previous_page_number()
            prev_page_url = '{}?page={}'.format(self.api_url, prev_page)
        else:
            prev_page_url = None

        return {
            'meta': {
                'limit': paginator.per_page,
                'next': next_page_url,
                'page': page.number,
                'previous': prev_page_url,
                'total_count': paginator.count
            },
            'items': page.object_list
        }
