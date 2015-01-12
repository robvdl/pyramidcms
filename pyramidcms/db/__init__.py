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
    def fields(self):
        """
        A property that returns all the fields for this model.

        :returns: a list of strings representing field names in the model.
        """
        return [col.name for col in class_mapper(self.__class__).mapped_table.c]

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

    def as_dict(self, full=True):
        """
        Returns this model instance as a dictionary.

        Many to many fields are returned as a list of id's unless
        full=True, in which case it recursively calls as_dict() on
        the related model instances which returns a list of dicts.

        :param full: when true recursively call as_dict() on sub-models.
        :returns: model instance converted to a dict
        """
        # This gets the normal fields but not many to many
        fields_dict = {col: getattr(self, col) for col in self.fields}

        # This contains all the fields including m2m fields.
        mapper = inspect(self.__class__)
        all_fields = [column.key for column in mapper.attrs]

        # Try to find m2m fields using the set difference,
        # ensure every field is actually an m2m field.
        possible_m2m = set(all_fields) - set(self.fields)
        for field_name in possible_m2m:
            field = getattr(self, field_name)
            if type(field) == InstrumentedList:
                if full:
                    fields_dict[field_name] = [model.as_dict() for model in field]
                else:
                    fields_dict[field_name] = [model.id for model in field]

        return fields_dict


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
"""DBSession is the SQLAlchemy database session instance."""

Base = declarative_base(cls=BaseModel)
"""Base is the SQLAlchemy declarative base instance."""

Model = Base
"""Model is just an alias of Base for convenience sake."""
