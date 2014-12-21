"""
This module contains the models required for users, groups and permissions.

The models are somewhat modelled after Django, but there are slight
differences, these differences are very minor though, so it should be
possible to import a user database from a Django site with minimal effort.
"""

from pyramidcms.models import Base

from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Boolean, Table, DateTime
from sqlalchemy.orm import relationship

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


class Permission(Base):
    """
    Based on the Django auth.Permission model, but with some key differences:

    * Renamed "codename" to "name" which is more consistent with other models
    * Renamed "name" to "description", also for consistency.
    * The "content_type" field is not used yet so is removed.
    """

    __tablename__ = 'permission'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(255))


class Group(Base):
    """
    Based on the Django auth.Group model, this model is basically the same.
    """

    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    permissions = relationship('Permission', secondary=group_permission_table)


class User(Base):
    """
    Based on the Django auth.User model, but with some key differences:

    * is_staff has been dropped, a permission is used instead for admin access
    * is_superuser and is_active just drop the "is_" prefix
    * permissions are only stored on the group to reduce the complexity
    """

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100))
    superuser = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    date_joined = Column(DateTime)
    last_login = Column(DateTime)
    groups = relationship('Group', secondary=user_group_table)

    def __init__(self, username, first_name=None, last_name=None, email=None, superuser=False):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.superuser = superuser

    def set_password(self, password):
        # TODO: use hash and salt
        self.password = password
