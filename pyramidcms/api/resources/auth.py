from colander import Schema, SchemaNode, Integer, String, Boolean, DateTime,\
    List, Length, drop

from pyramidcms.api import ModelApi, cms_resource
from pyramidcms.api.authorization import ACLAuthorization
from pyramidcms.api.authentication import SessionAuthentication
from pyramidcms.models import User, Group, Permission


class UserSchema(Schema):
    """
    Validation class for the UserApi resource.
    """
    id = SchemaNode(Integer(), missing=drop)
    username = SchemaNode(String(), validator=Length(max=50), missing=drop)
    first_name = SchemaNode(String(), validator=Length(max=50), missing=drop)
    last_name = SchemaNode(String(), validator=Length(max=50), missing=drop)
    email = SchemaNode(String(), validator=Length(max=50), missing=drop)
    password = SchemaNode(String(), validator=Length(max=100), missing=drop)
    is_active = SchemaNode(Boolean(), missing=drop)
    is_superuser = SchemaNode(Boolean(), missing=drop)
    date_joined = SchemaNode(DateTime(), missing=drop)
    last_login = SchemaNode(DateTime(), missing=drop)
    groups = SchemaNode(List(), missing=drop)


class GroupSchema(Schema):
    """
    Validation class for the GroupApi resource.
    """
    id = SchemaNode(Integer(), missing=drop)
    name = SchemaNode(String(), validator=Length(max=100), missing=drop)
    permissions = SchemaNode(List(), missing=drop)


class PermissionSchema(Schema):
    """
    Validation class for the PermissionApi resource.
    """
    id = SchemaNode(Integer(), missing=drop)
    name = SchemaNode(String(), validator=Length(max=50), missing=drop)
    description = SchemaNode(String(), validator=Length(max=255), missing=drop)


@cms_resource(resource_name='user')
class UserApi(ModelApi):
    class Meta:
        model = User
        schema = UserSchema
        authentication = SessionAuthentication()
        authorization = ACLAuthorization()


@cms_resource(resource_name='group')
class GroupApi(ModelApi):
    class Meta:
        model = Group
        schema = GroupSchema
        authentication = SessionAuthentication()
        authorization = ACLAuthorization()
        always_return_data = True


@cms_resource(resource_name='permission')
class PermissionApi(ModelApi):
    class Meta:
        model = Permission
        schema = PermissionSchema
        authentication = SessionAuthentication()
        authorization = ACLAuthorization()
