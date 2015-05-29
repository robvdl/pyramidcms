from pyramidcms.api import ModelApi, cms_resource
from pyramidcms.api.authorization import ACLAuthorization
from pyramidcms.api.authentication import SessionAuthentication
from pyramidcms.models import User, Group, Permission


@cms_resource(resource_name='user')
class UserApi(ModelApi):
    class Meta:
        model = User
        authentication = SessionAuthentication()
        authorization = ACLAuthorization()


@cms_resource(resource_name='group')
class GroupApi(ModelApi):
    class Meta:
        model = Group
        authentication = SessionAuthentication()
        authorization = ACLAuthorization()
        always_return_data = True


@cms_resource(resource_name='permission')
class PermissionApi(ModelApi):
    class Meta:
        model = Permission
        authentication = SessionAuthentication()
        authorization = ACLAuthorization()
