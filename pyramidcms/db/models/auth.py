from sqlalchemy import ForeignKey, func
from sqlalchemy import Column, Integer, String, Boolean, Table, DateTime
from sqlalchemy.orm import relationship
from passlib.hash import pbkdf2_sha256

from pyramidcms.db import DBSession, Base, Model, ModelManager

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
        return DBSession.query(Permission, Group).join(Group.permissions)


class Permission(Model):
    """
    Based on the Django auth.Permission model, but with some differences:

    * field names change: "name" and "description" are used for consistency
    * The "content_type" field has no real use to us so was removed.
    """
    name = Column(String(50), unique=True)
    description = Column(String(255))

    objects = PermissionManager()

    def __str__(self):
        return self.name


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

    * is_staff has been dropped, the Group/Permission system is used instead.
    * is_superuser has been renamed to just "superuser"
    * is_active has been renamed just "active"
    * permissions are only stored on the Group to reduce complexity

    In Django you can also set permissions on the User directly, but
    to keep things simple we only store these on the Group.
    """
    username = Column(String(50), nullable=False, unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100))
    password = Column(String(100))
    active = Column(Boolean, default=True)
    superuser = Column(Boolean, default=False)
    date_joined = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    groups = relationship('Group', secondary=user_group_table)

    def __str__(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        elif self.first_name:
            return self.first_name
        else:
            return self.username

    def is_active(self):
        """
        Returns user activity status.
        """
        return self.active

    def check_password(self, password):
        """
        Validate password against hashed password in database.
        """
        return pbkdf2_sha256.verify(password, self.password)

    def set_password(self, password):
        """
        Change the password for this user.
        """
        # pbkdf2 sha256 with a salt and 10k iterations is what Django uses
        self.password = pbkdf2_sha256.encrypt(password, rounds=10000)

    def get_permissions(self):
        """
        Returns a list of Permissions for this user based on their Groups.
        """
        group_ids = [group.id for group in self.groups]
        return DBSession.query(Permission).join(Group.permissions).filter(Group.id.in_(group_ids))
