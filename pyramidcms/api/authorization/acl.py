from pyramid.httpexceptions import HTTPForbidden

from .base import Authorization


class ACLAuthorization(Authorization):
    """
    Authorization class based on the Pyramid permission and ACL system.

    Checks for the permissions read-{resource}, update-{resource},
    create-{resource}, delete-{resource}.
    """

    def permission(self, action, bundle):
        """
        Returns a permission name based on the resource name and the action.

        :param action: can be 'read', 'create', 'update', or 'delete'
        :param bundle: API Bundle object
        :return: resource name plus an action, separated by a hyphen.
        """
        return '{}-{}'.format(action, bundle.resource.resource_name)

    def read_list(self, obj_list, bundle):
        if bundle.request.has_permission(self.permission('read', bundle)):
            return obj_list
        else:
            raise HTTPForbidden()

    def read_detail(self, obj, bundle):
        if bundle.request.has_permission(self.permission('read', bundle)):
            return True
        else:
            raise HTTPForbidden()

    def create_list(self, obj_list, bundle):
        if bundle.request.has_permission(self.permission('create', bundle)):
            return obj_list
        else:
            raise HTTPForbidden()

    def create_detail(self, obj, bundle):
        if bundle.request.has_permission(self.permission('create', bundle)):
            return True
        else:
            raise HTTPForbidden()

    def update_list(self, obj_list, bundle):
        if bundle.request.has_permission(self.permission('update', bundle)):
            return obj_list
        else:
            raise HTTPForbidden()

    def update_detail(self, obj, bundle):
        if bundle.request.has_permission(self.permission('update', bundle)):
            return True
        else:
            raise HTTPForbidden()

    def delete_list(self, obj_list, bundle):
        if bundle.request.has_permission(self.permission('delete', bundle)):
            return obj_list
        else:
            raise HTTPForbidden()

    def delete_detail(self, obj, bundle):
        if bundle.request.has_permission(self.permission('delete', bundle)):
            return True
        else:
            raise HTTPForbidden()
