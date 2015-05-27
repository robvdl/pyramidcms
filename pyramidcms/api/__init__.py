from cornice.resource import resource
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound, HTTPForbidden

from pyramidcms.api.authentication import Authentication
from pyramidcms.api.authorization import ReadOnlyAuthorization
from pyramidcms.core.paginator import Paginator
from pyramidcms.core.exceptions import InvalidPage
from pyramidcms.security import RootFactory


def get_global_acls(request):
    """
    Returns the global list of ACLs, already used by Pyramid views,
    by constructing the RootFactory object and returning __acl__.

    :param request: Pyramid request object
    :return: List of ACLs
    """
    return RootFactory(request).__acl__


def cms_resource(resource_name):
    """
    A helper that returns a cornice @resource decorator, pre-populating
    the collection_path, path, and name from the resource_name argument.

    :param resource_name: Name of the resource
    :return: @resource decorator
    """
    list_url = '/api/' + resource_name
    detail_url = list_url + '/{id:\d+}'

    return resource(
        name=resource_name,
        collection_path=list_url,
        path=detail_url,
        acl=get_global_acls
    )


class ApiMeta(object):
    """
    A configuration class for api resources ``BaseApi`` subclasses.

    Provides defaults and the logic needed to augment these settings with
    the internal ``class Meta`` used on ``ApiBase`` subclasses.

    Note that this is based on the ApiResource class from TastyPie,
    not everything is supported yet, this will be a gradual process.
    """
    paginator_class = Paginator
    allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
    list_allowed_methods = None
    detail_allowed_methods = None
    limit = 20
    max_limit = 1000
    filtering = {}
    ordering = []
    authentication = Authentication()
    authorization = ReadOnlyAuthorization()

    def __new__(cls, meta=None):
        overrides = {}

        # Handle overrides.
        if meta:
            for override_name in dir(meta):
                # No internals please.
                if not override_name.startswith('_'):
                    overrides[override_name] = getattr(meta, override_name)

        methods = overrides.get('allowed_methods',
                                ['get', 'post', 'put', 'delete', 'patch'])

        if overrides.get('list_allowed_methods') is None:
            overrides['list_allowed_methods'] = methods

        if overrides.get('detail_allowed_methods') is None:
            overrides['detail_allowed_methods'] = methods

        return object.__new__(type('ApiMeta', (cls,), overrides))


class DeclarativeMetaclass(type):

    def __new__(mcs, name, bases, attrs):
        new_class = super(DeclarativeMetaclass, mcs).__new__(mcs, name, bases, attrs)
        meta = getattr(new_class, 'Meta', None)
        new_class._meta = ApiMeta(meta)

        return new_class


class ApiBase(object, metaclass=DeclarativeMetaclass):
    """
    The ``ApiBase`` class is for building RESTful resources using the
    Mozilla Cornice library.  Originally the design was modelled a bit
    after TastyPie, a RESTful API library for Django.

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

    def __init__(self, request):
        self.request = request

    @reify
    def api_url(self):
        key = [s for s in self._services if s.startswith('collection_')][0]
        return self._services[key].path

    @reify
    def resource_name(self):
        key = [s for s in self._services if not s.startswith('collection_')][0]
        return self._services[key].name

    @reify
    def paginator(self):
        return self._meta.paginator_class(self.get_allowed_objects(), self._meta.limit)

    def get_allowed_objects(self):
        """
        This method filters the objects coming from the :meth:`get_obj_list()`
        method using the authorization class read_list() method.
        """
        return self._meta.authorization.read_list(self.get_obj_list(), self)

    def get_obj_list(self):
        """
        The get_obj_list method must return a list of items for this
        API resource, this can be a SQLAlchemy queryset.
        """
        raise NotImplementedError

    def get_obj(self, obj_id):
        raise NotImplementedError

    def dehydrate(self, obj):
        return obj

    def hydrate(self, obj):
        return obj

    def get(self):
        if self._meta.authentication.is_authenticated(self.request):
            obj = self.get_obj(int(self.request.matchdict['id']))

            # check if we have read access to this object
            if self._meta.authorization.read_detail(obj, self):
                return self.dehydrate(obj)
            else:
                raise HTTPForbidden()
        else:
            raise HTTPForbidden()

    def collection_get(self):
        """
        The API collection_get method is used by Cornice, it returns a list
        of items for this API class.
        """
        if self._meta.authentication.is_authenticated(self.request):
            # authorization (filtering results) happens in paginator property
            try:
                page_number = int(self.request.GET.get('page', 1))
                page = self.paginator.page(page_number)
            except (ValueError, InvalidPage):
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
                    'limit': self.paginator.per_page,
                    'next': next_page_url,
                    'page': page.number,
                    'num_pages': self.paginator.num_pages,
                    'previous': prev_page_url,
                    'total_count': self.paginator.count
                },
                'items': [self.dehydrate(obj) for obj in page.object_list]
            }
        else:
            raise HTTPForbidden()


class Api(ApiBase):
    """
    The regular ``Api`` class is for building API resources for non-model
    data, it is similar to the regular Resource class in TastyPie.
    """

    def get_obj_list(self):
        return []

    def get_obj(self, obj_id):
        return {}


class ModelApi(ApiBase):
    """
    The ``ModelApi`` class is for building API resources for SQL Alchemy
    models, it is similar to the ModelResource class in TastyPie.
    """

    def get_obj_list(self):
        """
        For a ``ModelApi``, get_obj_list returns a queryset, so when we get
        to do the pagination it can apply a LIMIT to the query rather than
        fetching all the rows.
        """
        return self._meta.model.objects.all()

    def get_obj(self, obj_id):
        obj = self._meta.model.objects.get(id=obj_id)
        if obj is None:
            raise HTTPNotFound()
        return obj

    def dehydrate(self, obj):
        return obj.serialize()
