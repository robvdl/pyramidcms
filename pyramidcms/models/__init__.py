from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


class BaseModel(object):
    """
    Base class for all models.

    Works a little like Django models, but using SQL Alchemy.

    This class actually gets mixed in when we create our declarative_base
    instance using the cls argument.  This makes any methods defined here
    available to every model automatically.

    see: http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html#augmenting-the-base
    """

    # By default every model uses id for the primary key.
    # This makes shared model code a bit easier to deal with.
    id = Column(Integer, primary_key=True)

    def delete(self):
        self.objects.filter(id=self.id).delete()

    def save(self):
        DBSession.add(self)


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base(cls=BaseModel)
Model = Base  # Model is just an alias of Base
