from pyramid.httpexceptions import HTTPForbidden

from .base import Authorization


class ACLAuthorization(Authorization):
    """
    Authorization class based on the Pyramid permission and ACL system.

    Checks for the permissions read-{resource}, update-{resource},
    create-{resource}, delete-{resource}.
    """

    def permission(self, action, resource):
        """
        Returns a permission name based on the resource name and the action.

        :param action: can be 'read', 'create', 'update', or 'delete'
        :param resource: api resource inheriting :class:`pyramidcms.api.ApiBase`
        :return: resource name plus and action, separated by a hyphen.
        """
        return '{}-{}'.format(action, resource.resource_name)

    def read_list(self, obj_list, resource):
        if resource.request.has_permission(self.permission('read', resource)):
            return obj_list
        else:
            raise HTTPForbidden()

    def read_detail(self, obj, resource):
        if resource.request.has_permission(self.permission('read', resource)):
            return True
        else:
            raise HTTPForbidden()

    def create_list(self, obj_list, resource):
        if resource.request.has_permission(self.permission('create', resource)):
            return obj_list
        else:
            raise HTTPForbidden()

    def create_detail(self, obj, resource):
        if resource.request.has_permission(self.permission('create', resource)):
            return True
        else:
            raise HTTPForbidden()

    def update_list(self, obj_list, resource):
        if resource.request.has_permission(self.permission('update', resource)):
            return obj_list
        else:
            raise HTTPForbidden()

    def update_detail(self, obj, resource):
        if resource.request.has_permission(self.permission('update', resource)):
            return True
        else:
            raise HTTPForbidden()

    def delete_list(self, obj_list, resource):
        if resource.request.has_permission(self.permission('delete', resource)):
            return obj_list
        else:
            raise HTTPForbidden()

    def delete_detail(self, obj, resource):
        if resource.request.has_permission(self.permission('delete', resource)):
            return True
        else:
            raise HTTPForbidden()
