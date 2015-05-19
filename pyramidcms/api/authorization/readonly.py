from pyramid.httpexceptions import HTTPForbidden

from .base import Authorization


class ReadOnlyAuthorization(Authorization):
    """
    Basic authorization class that only allows read and read_list.

    This is the default authorization class.
    """

    def create_list(self, obj_list, resource):
        raise HTTPForbidden()

    def create_detail(self, obj, resource):
        raise HTTPForbidden()

    def update_list(self, obj_list, resource):
        raise HTTPForbidden()

    def update_detail(self, obj, resource):
        raise HTTPForbidden()

    def delete_list(self, obj_list, resource):
        raise HTTPForbidden()

    def delete_detail(self, obj, resource):
        raise HTTPForbidden()
