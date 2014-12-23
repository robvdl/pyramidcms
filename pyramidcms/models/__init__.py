from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


class ModelManager(object):
    """
    Base model manager class for all models.
    """

    def __init__(self):
        self.model = None

    def all(self):
        return DBSession.query(self.model)

    def create(self, *args, **kwargs):
        obj = self.model(*args, **kwargs)
        obj.save()

    def filter(self, **kwargs):
        return DBSession.query(self.model).filter_by(**kwargs)

    def get(self, **kwargs):
        return self.filter(**kwargs).first()

    def count(self):
        return DBSession.query(self.model).count()


class BaseModel(object):
    """
    Base class for all models.

    Works a little like Django models, but using SQL Alchemy.

    This class actually gets mixed in when we create our declarative_base
    instance using the cls argument.  This makes any methods defined here
    available to every model automatically.

    see: http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html#augmenting-the-base

    By default every model uses id for the primary key, this makes shared
    model code a bit easier to deal with.
    """
    id = Column(Integer, primary_key=True)
    objects = ModelManager()

    def __init__(self):
        self.objects.model = self

    @declared_attr
    def __tablename__(cls):
        """
        This gives a default table name which is just the model class
        name as lower case, can still be overridden however.
        """
        return cls.__name__.lower()

    def delete(self):
        self.objects.filter(id=self.id).delete()

    def save(self):
        DBSession.add(self)


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base(cls=BaseModel)
Model = Base  # Model is just an alias of Base
