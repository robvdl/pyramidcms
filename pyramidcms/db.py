import re
import datetime
import transaction

from sqlalchemy import Column, Integer, inspect, engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from zope.sqlalchemy import ZopeTransactionExtension

# this regex is used to convert camelcase model names to table names
RE_CAMELCASE = re.compile(r'([A-Z]+)(?=[a-z0-9])')


def setup_db_connection(settings):
    """
    Initialises the database connection.

    :param settings: Pyramid settings object
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine


class ModelManager(object):
    """
    Default model manager class for all models.

    To add new methods, a model may choose to subclass the ModelManager
    class, though this is completely optional.
    """

    def __init__(self, model=None):
        """
        Default model manager constructor.

        This sets self.model to None as we don't know the model yet
        at this point, this gets filled in elsewhere.

        It is also possible to pass a model to the constructor, at the
        moment this is only used during tests, but this may change.
        """
        self.model = model

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

        The default is to lowercase the model name and use underscores
        between words rather than camelcase.
        """
        def _join(match):
            word = match.group()
            if len(word) > 1:
                return '_{}_{}'.format(word[:-1], word[-1]).lower()
            return '_' + word.lower()

        return RE_CAMELCASE.sub(_join, cls.__name__).lstrip('_')

    def __str__(self):
        """
        Should be implemented in each model, we do need it here though,
        or we get a recursion loop going when calling __repr__.
        """
        return str(self.id)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)

    @property
    def db_columns(self):
        """
        Returns a list of database column names.

        This returns only actual database columns, so many to many
        fields will not be included in the list.

        :returns: a list of database column names for this model
        """
        mapper = inspect(self.__class__)
        return [col.name for col in mapper.mapped_table.c]

    @property
    def orm_fields(self):
        """
        Returns a list of model fields for serialization.

        For foreign keys, we only include the relationship part, not
        the actual field, which is what the db_columns property is for.

        The list of fields also includes many-to-many relationships but
        for backrefs we don't include the "other side" of the relationship,
        or we end up going in loops when doing a serialize with full=True.

        :return: a list of fields for this model.
        """
        mapper = inspect(self.__class__)
        fields = []

        # regular fields
        for col in mapper.columns:
            # exclude foreign key fields, as we use the relationships instead
            if not col.foreign_keys:
                fields.append(col)

        # relationship fields
        for rel in mapper.relationships:
            # exclude fields added by backrefs that cause serialization issues
            if not (rel.backref is None and rel.back_populates):
                fields.append(rel)

        return fields

    def delete(self):
        """
        Deletes the current instance of this model from the database.
        """
        self.objects.filter(id=self.id).delete()

    def save(self, commit=False):
        """
        Save current model instance to database.

        This just wraps the DBSession.add() function from SQLAlchemy.

        :param commit: Will also commit transaction (required in pcms shell)
        """
        DBSession.add(self)

        # Manually commit, this is probably going to be a temporary thing.
        # When in "pcms shell", after .save() we must manually commit.
        if commit:
            transaction.commit()

    def serialize(self, full=False):
        """
        Returns this model instance as a dictionary.

        Many to many fields are returned as a list of id's unless
        full=True, in which case it recursively calls serialize() on
        the related model instances which returns a list of dicts.

        Date fields are converted into a string using ISO format,
        so that a serialized model can easily be converted to JSON.

        :param full: when true recursively call serialize() on sub-models.
        :returns: model instance serialized into a dict.
        """
        fields_dict = {}
        for field in self.orm_fields:
            field_name = field.key
            value = getattr(self, field_name)

            # foreign keys
            if isinstance(value, Model):
                if full:
                    fields_dict[field_name] = value.serialize(full=True)
                else:
                    fields_dict[field_name] = value.id

            # many to many
            elif type(value) == InstrumentedList:
                if full:
                    fields_dict[field_name] = [model.serialize(full=True)
                                               for model in value]
                else:
                    fields_dict[field_name] = [model.id for model in value]

            # regular fields
            elif type(value) == datetime.datetime or type(value) == datetime.date:
                fields_dict[field_name] = value.isoformat()  # encode dates
            else:
                fields_dict[field_name] = value

        return fields_dict


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
"""DBSession is the SQLAlchemy database session instance."""

Base = declarative_base(cls=BaseModel)
"""Base is the SQLAlchemy declarative base instance."""

Model = Base
"""Model is just an alias of Base for convenience sake."""
