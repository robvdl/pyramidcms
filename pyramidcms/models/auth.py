import hashlib

from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Boolean, Table, DateTime
from sqlalchemy.orm import relationship

from pyramidcms.models import Base, Model, ModelManager, DBSession

# bridge tables
group_permission_table = Table(
    'group_permission', Base.metadata,
    Column('group_id', Integer, ForeignKey('group.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permission.id'), primary_key=True)
)

user_group_table = Table(
    'user_group', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('group.id'), primary_key=True)
)


class PermissionManager(ModelManager):
    """
    Model-manager class for the Permission model.
    """

    def list_by_group(self):
        """
        Returns a list of tuples (Permission, Group), only returns rows where
        permissions are used by a group.
        """
        return DBSession.query(Permission, Group).join((Permission, Group.permissions))


class Permission(Model):
    """
    Based on the Django auth.Permission model, but with some differences:

    * The "content_type" field is not used yet so is removed.
    """
    name = Column(String(255))
    codename = Column(String(50), unique=True)

    objects = PermissionManager()

    def __str__(self):
        return self.description


class Group(Model):
    """
    Based on the Django auth.Group model, this model is basically the same.
    """
    name = Column(String(100), unique=True)
    permissions = relationship('Permission', secondary=group_permission_table)

    def __str__(self):
        return self.name


class User(Model):
    """
    Based on the Django auth.User model, but with some differences:

    * is_staff becomes is_admin which gives basic admin access
    * permissions are only stored on the group to reduce the complexity

    Note that when "is_superuser" is set, this implies you have "is_admin"
    as well to the permission system, even if is_admin is false on the user.
    """
    username = Column(String(50), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100))
    password = Column(String(200))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    date_joined = Column(DateTime)
    last_login = Column(DateTime)
    groups = relationship('Group', secondary=user_group_table)

    def __str__(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        elif self.first_name:
            return self.first_name
        else:
            return self.username

    def check_password(self, password):
        return self.password == hashlib.sha512(password.encode('utf-8')).hexdigest()

    def set_password(self, password):
        """
        Change the password for this user.
        """
        # TODO: SHA512 is OK but the hashes are huge (and why field size is 200)
        # TODO: add support for salt.
        self.password = hashlib.sha512(password.encode('utf-8')).hexdigest()

    def get_permissions(self):
        """
        Returns a list of Permissions for this user based on their Groups.
        """
        group_ids = [group.id for group in self.groups]
        return DBSession.query(Permission).join((Permission, Group.permissions)).filter(Group.id.in_(group_ids))


# TODO: how can we bootstrap this?
Permission.objects.model = Permission
Group.objects.model = Group
User.objects.model = User
