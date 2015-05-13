from . import BaseAuthorization


class ACLAuthorization(BaseAuthorization):

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
            return []

    def read_detail(self, obj):
        return self.resource.request.has_permission(self.permission('read'))

    def create_list(self, obj_list):
        if self.resource.request.has_permission(self.permission('create')):
            return obj_list
        else:
            return []

    def create_detail(self, obj):
        return self.resource.request.has_permission(self.permission('create'))

    def update_list(self, obj_list):
        if self.resource.request.has_permission(self.permission('update')):
            return obj_list
        else:
            return []

    def update_detail(self, obj):
        return self.resource.request.has_permission(self.permission('update'))

    def delete_list(self, obj_list):
        if self.resource.request.has_permission(self.permission('delete')):
            return obj_list
        else:
            return []

    def delete_detail(self, obj):
        return self.resource.request.has_permission(self.permission('delete'))
