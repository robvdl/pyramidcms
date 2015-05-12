from pyramidcms.api import ModelApi, cms_resource
from pyramidcms.api.authorization.acl import ACLAuthorization
from pyramidcms.models import User, Group, Permission


@cms_resource(resource_name='user')
class UserApi(ModelApi):
    class Meta:
        model = User
        authorization = ACLAuthorization()
        limit = 0


@cms_resource(resource_name='group')
class GroupApi(ModelApi):
    class Meta:
        model = Group


@cms_resource(resource_name='permission')
class PermissionApi(ModelApi):
    class Meta:
        model = Permission
