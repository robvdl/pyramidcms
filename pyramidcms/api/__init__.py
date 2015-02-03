from pyramidcms.core.paginator import Paginator


class ApiBase(object):

    _services = None

    class Meta:
        limit = 20

    def __init__(self, request):
        self.request = request
        self.meta = self.Meta()
        self.api_url = self._get_api_url()
