from pyramid.httpexceptions import HTTPForbidden

from .base import Authorization


class ACLAuthorization(Authorization):
    """
    Authorization class based on the Pyramid permission and ACL system.

    Checks for the permissions read-{resource}, update-{resource},
    create-{resource}, delete-{resource}.
    """

    def permission(self, action):
        """
        Returns a permission name based on the resource name and the action.

        :param action: can be 'read', 'create', 'update', or 'delete'
        :return: resource name plus and action, separated by a hyphen.
        """
        return '{}-{}'.format(action, self.resource.resource_name)

    def read_list(self, obj_list):
        if self.resource.request.has_permission(self.permission('read')):
            return obj_list
        else:
            raise HTTPForbidden()

    def read_detail(self, obj):
        if self.resource.request.has_permission(self.permission('read')):
            return True
        else:
            raise HTTPForbidden()

    def create_list(self, obj_list):
        if self.resource.request.has_permission(self.permission('create')):
            return obj_list
        else:
            raise HTTPForbidden()

    def create_detail(self, obj):
        if self.resource.request.has_permission(self.permission('create')):
            return True
        else:
            raise HTTPForbidden()

    def update_list(self, obj_list):
        if self.resource.request.has_permission(self.permission('update')):
            return obj_list
        else:
            raise HTTPForbidden()

    def update_detail(self, obj):
        if self.resource.request.has_permission(self.permission('update')):
            return True
        else:
            raise HTTPForbidden()

    def delete_list(self, obj_list):
        if self.resource.request.has_permission(self.permission('delete')):
            return obj_list
        else:
            raise HTTPForbidden()

    def delete_detail(self, obj):
        if self.resource.request.has_permission(self.permission('delete')):
            return True
        else:
            raise HTTPForbidden()
