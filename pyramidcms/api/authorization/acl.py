from . import BaseAuthorization


class ACLAuthorization(BaseAuthorization):

    def read_detail(self, obj):
        permission = 'read-{}'.format(self.resource.resource_name)
        return self.resource.request.has_permission(permission)
