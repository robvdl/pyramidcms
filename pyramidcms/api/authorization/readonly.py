from pyramid.httpexceptions import HTTPForbidden

from .base import Authorization
from pyramidcms.core.messages import NOT_AUTHORIZED


class ReadOnlyAuthorization(Authorization):
    """
    Basic authorization class that only allows read and read_list.

    This is the default authorization class.
    """

    def create_list(self, obj_list, bundle):
        raise HTTPForbidden(NOT_AUTHORIZED)

    def create_detail(self, obj, bundle):
        raise HTTPForbidden(NOT_AUTHORIZED)

    def update_list(self, obj_list, bundle):
        raise HTTPForbidden(NOT_AUTHORIZED)

    def update_detail(self, obj, bundle):
        raise HTTPForbidden(NOT_AUTHORIZED)

    def delete_list(self, obj_list, bundle):
        raise HTTPForbidden(NOT_AUTHORIZED)

    def delete_detail(self, obj, bundle):
        raise HTTPForbidden(NOT_AUTHORIZED)
