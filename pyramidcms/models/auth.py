import hashlib

from pyramidcms.models import Base, DBSession

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


# TODO: there is a lot of boilerplate in the models and model manager classes
# that are repeated for each model, we need a way to abstract this into a
# common base class (just called ModelManager), before we get too many models.

class PermissionManager(object):
    """
    A Django-style model-manager class for the Permission model.
    """

    def all(self):
        return DBSession.query(Permission)

    def create(self, *args, **kwargs):
        permission = Permission(*args, **kwargs)
        permission.save()

    def filter(self, **kwargs):
        return DBSession.query(Permission).filter_by(**kwargs)

    def get(self, **kwargs):
        return self.filter(**kwargs).first()

    def count(self):
        return DBSession.query(Permission).count()


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

    # model-manager class
    objects = PermissionManager()

    def delete(self):
        self.objects.filter(id=self.id).delete()

    def save(self):
        DBSession.add(self)


class GroupManager(object):
    """
    A Django-style model-manager class for the Group model.
    """

    def all(self):
        return DBSession.query(Group)

    def create(self, *args, **kwargs):
        group = Group(*args, **kwargs)
        group.save()

    def filter(self, **kwargs):
        return DBSession.query(Group).filter_by(**kwargs)

    def get(self, **kwargs):
        return self.filter(**kwargs).first()

    def count(self):
        return DBSession.query(Group).count()


class Group(Base):
    """
    Based on the Django auth.Group model, this model is basically the same.
    """

    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    permissions = relationship('Permission', secondary=group_permission_table)

    # model-manager class
    objects = GroupManager()

    def delete(self):
        self.objects.filter(id=self.id).delete()

    def save(self):
        DBSession.add(self)


class UserManager(object):
    """
    A Django-style model-manager class for the User model.
    """

    def all(self):
        return DBSession.query(User)

    def create(self, *args, **kwargs):
        user = User(*args, **kwargs)
        user.save()

    def filter(self, **kwargs):
        return DBSession.query(User).filter_by(**kwargs)

    def get(self, **kwargs):
        return self.filter(**kwargs).first()

    def count(self):
        return DBSession.query(User).count()


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
    password = Column(String(200))
    superuser = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    date_joined = Column(DateTime)
    last_login = Column(DateTime)
    groups = relationship('Group', secondary=user_group_table)

    # model-manager class
    objects = UserManager()

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

    def delete(self):
        self.objects.filter(id=self.id).delete()

    def save(self):
        DBSession.add(self)
