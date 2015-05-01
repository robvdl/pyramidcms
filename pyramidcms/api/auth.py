from cornice.resource import resource

from pyramidcms.api import ModelApi
from pyramidcms.models import User, Group, Permission


@resource(collection_path='/api/user', path='/api/user/{id}')
class UserApi(ModelApi):
    class Meta:
        model = User
        limit = 0


@resource(collection_path='/api/group', path='/api/group/{id}')
class GroupApi(ModelApi):
    class Meta:
        model = Group


@resource(collection_path='/api/permission', path='/api/permission/{id}')
class PermissionApi(ModelApi):
    class Meta:
        model = Permission
