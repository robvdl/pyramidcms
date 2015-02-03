from pyramidcms.core.paginator import Paginator


class ApiBase(object):

    _services = None

    class Meta:
        limit = 20

    def __init__(self, request):
        self.request = request
        self.meta = self.Meta()
        self.api_url = self._get_api_url()

    def _get_api_url(self):
        key = [s for s in self._services if s.startswith('collection_')][0]
        return self._services[key].path

    def obj_list(self):
        return []

    def collection_get(self):
        paginator = Paginator(self.obj_list(), self.meta.limit)
        page = paginator.page(1)

        if page.has_next():
            page_ofs = page.next_page_offset()
            next_page_url = '{0}?offset={1}'.format(self.api_url, page_ofs)
        else:
            next_page_url = None

        if page.has_previous():
            page_ofs = page.prev_page_offset()
            prev_page_url = '{0}?offset={1}'.format(self.api_url, page_ofs)
        else:
            prev_page_url = None

        return {
            'meta': {
                'limit': paginator.per_page,
                'next': next_page_url,
                'offset': page.offset,
                'previous': prev_page_url,
                'total_count': paginator.count
            },
            'items': page.object_list
        }
