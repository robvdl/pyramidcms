import hashlib

from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Boolean, Table, DateTime
from sqlalchemy.orm import relationship

from pyramidcms.models import Base, Model, ModelManager

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


class Permission(Model):
    """
    Based on the Django auth.Permission model, but with some key differences:

    * Renamed "codename" to "name" which is more consistent with other models
    * Renamed "name" to "description", also for consistency.
    * The "content_type" field is not used yet so is removed.
    """

    __tablename__ = 'permission'
    name = Column(String(50), unique=True)
    description = Column(String(255))

    # model-manager class
    objects = ModelManager()


class Group(Model):
    """
    Based on the Django auth.Group model, this model is basically the same.
    """

    __tablename__ = 'group'
    name = Column(String(100), unique=True)
    permissions = relationship('Permission', secondary=group_permission_table)

    # model-manager class
    objects = ModelManager()


class User(Model):
    """
    Based on the Django auth.User model, but with some key differences:

    * is_staff has been dropped, a permission is used instead for admin access
    * is_superuser and is_active just drop the "is_" prefix
    * permissions are only stored on the group to reduce the complexity
    """

    __tablename__ = 'user'
    username = Column(String(50), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100))
    password = Column(String(200))
    superuser = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    date_joined = Column(DateTime)
    last_login = Column(DateTime)
    groups = relationship('Group', secondary=user_group_table)

    # model-manager class
    objects = ModelManager()

    def __init__(self, username, first_name=None, last_name=None, email=None, superuser=False):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.superuser = superuser

    def check_password(self, password):
        return self.password == hashlib.sha512(password.encode('utf-8')).hexdigest()

    def set_password(self, password):
        """
        Change the password for this user.
        """
        # TODO: SHA512 is OK but the hashes are huge (and why field size is 200)
        # TODO: add support for salt.
        self.password = hashlib.sha512(password.encode('utf-8')).hexdigest()


# TODO: how can we bootstrap this?
Permission.objects.model = Permission
Group.objects.model = Group
User.objects.model = User
