from pyramidcms.api import ModelApi, cms_resource
from pyramidcms.api.authorization import ACLAuthorization
from pyramidcms.api.authentication import SessionAuthentication
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
        authentication = SessionAuthentication()


@cms_resource(resource_name='permission')
class PermissionApi(ModelApi):
    class Meta:
        model = Permission
