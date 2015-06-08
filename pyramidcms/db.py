import re
import datetime
import transaction

from sqlalchemy import inspect, engine_from_config
from sqlalchemy import Column, Integer
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

    def get_column_for_attr(self, attr):
        """
        Given the attribute, try to find the matching column object.

        This is easy to do for regular ColumnProperty types, but a
        bit trickier with relationships and depends on the type
        of the relationship.
        """
        if attr.__class__.__name__ == 'ColumnProperty':
            return attr.columns[0]

        # Older versions of SQL Alchemy use RelationProperty
        elif attr.__class__.__name__ in ('RelationProperty', 'RelationshipProperty'):
            relation_type = attr.direction.name
            if relation_type == 'MANYTOONE':
                # many to one has a matching column on the model,
                # e.g. the "user" relation might have a "user_id" column.
                return list(attr.local_columns)[0]
            elif relation_type == 'MANYTOMANY':
                # m2m has no matching column on the model
                return None
            else:
                # this could happen when we get a relationship type
                # that we haven't dealt with yet in serialization.
                raise TypeError('Cannot handle relationship type: ' + relation_type)

        else:
            # this should never happen
            raise TypeError('Unknown attribute type')

    @property
    def orm_fields(self):
        """
        Returns a list of field tuples for this model, in the form
        of (attr, column).

        Since foreign keys are done across two fields in SQL Alchemy,
        for example "user_id" for the actual field, and "user" for the
        relation, we only include "user" in the list and not "user_id".
        The list of fields also includes many-to-many relationships.

        :return: a list of field tuples for this model.
        """
        mapper = inspect(self.__class__)

        fields = []
        for attr in mapper.attrs:
            # Try to get the matching column object for this attribute.
            col = self.get_column_for_attr(attr)

            # Older versions of SQL Alchemy use RelationProperty
            if attr.__class__.__name__ in ('RelationProperty', 'RelationshipProperty'):
                # If backref is None and back_populates set, this is a backref
                # which we won't return to avoid going round in circles.
                if attr.backref is None and attr.back_populates is not None:
                    continue

            elif attr.__class__.__name__ == 'ColumnProperty':
                # Don't include foreign key fields directly like "user_id",
                # these are already handled by the relationship "user" instead.
                if col.foreign_keys:
                    continue

            else:
                raise TypeError('Unknown attribute type')

            fields.append((attr, col))

        return fields

    def delete(self):
        """
        Deletes the current instance of this model from the database.
        """
        self.objects.filter(id=self.id).delete()

    def save(self, flush=False, commit=False):
        """
        Save current model instance to database.

        This just wraps the DBSession.add() function from SQLAlchemy.

        :param flush: Will also flush the DBSession (used by API)
        :param commit: Will also commit transaction (required in pcms shell)
        """
        DBSession.add(self)

        # This is used by the API to save the object before pyramid_tm
        if flush:
            DBSession.flush()

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

        for attr, column in self.orm_fields:
            attr_name = attr.key
            value = getattr(self, attr_name)

            # foreign keys
            if isinstance(value, Model):
                if full:
                    fields_dict[attr_name] = value.serialize(full=True)
                else:
                    fields_dict[attr_name] = value.id

            # many to many
            elif type(value) == InstrumentedList:
                if full:
                    fields_dict[attr_name] = [model.serialize(full=True) for model in value]
                else:
                    fields_dict[attr_name] = [model.id for model in value]

            # regular fields
            elif type(value) in (datetime.datetime, datetime.date):
                fields_dict[attr_name] = value.isoformat()  # encode dates
            else:
                fields_dict[attr_name] = value

        return fields_dict

    def deserialize(self, data):
        """
        Simple deserialize previously serialized data into current
        model instance.

        Note that the data dict going in, is expected to come from
        Colander Schema from the API, so we shouldn't need to do
        any field type conversion here.

        :param data: dictionary of data from a Colander Schema.
        """
        decoded_data = {}
        model_fields = self.orm_fields

        # copy only model fields, no conversion should be necessary
        for attr, column in model_fields:
            if attr.key in data:
                decoded_data[attr.key] = data[attr.key]

        # update model instance fields
        for k, v in decoded_data.items():
            setattr(self, k, v)

    def __json__(self, request):
        """
        Allows returning of a model instance from a view and it will
        automatically get serialized.

        :param request: Pyramid request object
        :return: dictionary of serialized model instance
        """
        return self.serialize()


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
"""DBSession is the SQLAlchemy database session instance."""

Base = declarative_base(cls=BaseModel)
"""Base is the SQLAlchemy declarative base instance."""

Model = Base
"""Model is just an alias of Base for convenience sake."""
