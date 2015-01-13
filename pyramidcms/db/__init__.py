from datetime import datetime

from sqlalchemy import Column, Integer, inspect
from sqlalchemy.orm import scoped_session, sessionmaker, class_mapper
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from zope.sqlalchemy import ZopeTransactionExtension


class ModelManager(object):
    """
    Default model manager class for all models.

    To add new methods, a model may choose to subclass the ModelManager
    class, though this is completely optional.
    """

    def __init__(self):
        """
        Default model manager constructor.

        This sets self.model to None as we don't know the model yet
        at this point, this gets filled in elsewhere.
        """
        self.model = None

    def all(self):
        """
        Query that return all rows for the current model.
        """
        return DBSession.query(self.model)

    def create(self, *args, **kwargs):
        """
        Create a new instance of the current model and call save().
        """
        # noinspection PyCallingNonCallable
        obj = self.model(*args, **kwargs)
        obj.save()
        return obj

    def filter(self, **kwargs):
        """
        Filter by keyword arguments, simply calls the filter_by() method
        from SQLAlchemy.
        """
        return DBSession.query(self.model).filter_by(**kwargs)

    def get(self, **kwargs):
        """
        Query that returns the first record based on the filter defined
        by kwargs.
        """
        return self.filter(**kwargs).first()

    def count(self):
        """
        Returns the total number of rows for the current model.
        """
        return DBSession.query(self.model).count()


class BaseModel(object):
    """
    Base class for all models.

    Works a little like Django models, but using SQL Alchemy.

    This class actually gets mixed in when we create our declarative_base
    instance using the cls argument.  This makes any methods defined here
    available to every model automatically.

    By default every model uses id for the primary key, this makes shared
    model code a bit easier to deal with.
    """
    id = Column(Integer, primary_key=True)

    @declared_attr
    def objects(cls):
        """
        The objects property returns the default ModelManager() instance,
        though this can be overridden in models if desired.

        :param cls: The model class
        """
        return ModelManager()

    @declared_attr
    def __tablename__(cls):
        """
        This gives a default table name which is just the model class
        name as lower case, can still be overridden however.
        """
        return cls.__name__.lower()

    @property
    def columns(self):
        """
        A property that returns all the actual db columns for this model.

        This does not include many to many, since these are not actual
        fields in the database.

        :returns: a list of columns for the model table.
        """
        return [col.name for col in class_mapper(self.__class__).mapped_table.c]

    @property
    def fields(self):
        """
        This returns all fields for this model.

        That means for the foreign key for example: "user_id" and the
        matching relation field "user", we return "user" but not
        "user_id" which gets filtered out.

        This also includes many to many relationship fields.

        :return: a list of field names for this model.
        """
        mapper = inspect(self.__class__)

        fields_list = []
        for col in mapper.attrs:
            column = getattr(self.__class__, col.key)
            foreign_keys = getattr(column, 'foreign_keys', None)

            # don't include foreign key columns like user_id
            if not foreign_keys:
                fields_list.append(col.key)

        return fields_list

    def delete(self):
        """
        Deletes the current instance of this model from the database.
        """
        self.objects.filter(id=self.id).delete()

    def save(self):
        """
        Save current model instance to database.

        This just wraps the DBSession.add() function from SQLAlchemy.
        """
        DBSession.add(self)

    def serialize(self, full=False):
        """
        Returns this model instance as a dictionary.

        Many to many fields are returned as a list of id's unless
        full=True, in which case it recursively calls serialize() on
        the related model instances which returns a list of dicts.

        Date fields are converted into a string using ISO format,
        so that a serialized model can easily be converted to JSON.

        :param full: when true recursively call serialize() on sub-models.
        :returns: model instance serialized into a dict
        """
        fields_dict = {}
        for field_name in self.fields:
            field = getattr(self, field_name)

            # foreign keys
            if isinstance(field, Model):
                if full:
                    fields_dict[field_name] = field.serialize()
                else:
                    fields_dict[field_name] = field.id

            # many to many
            elif type(field) == InstrumentedList:
                if full:
                    fields_dict[field_name] = [model.serialize(True) for model in field]
                else:
                    fields_dict[field_name] = [model.id for model in field]

            # regular fields
            elif type(field) == datetime:
                fields_dict[field_name] = field.isoformat()  # encode dates
            else:
                fields_dict[field_name] = field

        return fields_dict


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
"""DBSession is the SQLAlchemy database session instance."""

Base = declarative_base(cls=BaseModel)
"""Base is the SQLAlchemy declarative base instance."""

Model = Base
"""Model is just an alias of Base for convenience sake."""
