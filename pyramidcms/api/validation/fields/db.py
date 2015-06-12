import colander
from sqlalchemy import String, Text, Integer, inspect

from pyramidcms.db import DBSession


class DBField(colander.SchemaType):
    """
    Base class for database field, for shared methods.
    """

    def __init__(self, model):
        self.model = model
        self.pk = self.get_pk()
        self.type = type(self.pk.type)

    def get_pk(self):
        """
        :returns: the primary key field for this model.
        """
        mapper = inspect(self.model)
        attr = mapper.attrs['id']
        return self.model.get_field_for_attr(attr)


class ForeignKey(DBField):
    """
    A colander field for foreign keys, supports either integer or string
    based foreign keys.

    The field will do a database query to ensure the foreign key exists first.
    """

    def __init__(self, model, **kwargs):
        super().__init__(model)

        if self.type in (String, Text):
            self.field = colander.String(**kwargs)
        elif self.type is Integer:
            self.field = colander.Integer()
        else:
            raise ValueError('Foreign key of type {} not supported'.format(self.type))

    def serialize(self, node, appstruct):
        """
        Serialize must do the opposite to deserialize, which is basically
        to return the model instance id back.

        :param node: :class:`colander.SchemaNode`
        :param appstruct: Model instance
        :return: Model instance id
        """
        if appstruct is colander.null:
            return appstruct

        if self.type in (String, Text):
            return str(appstruct.id)
        elif self.type is Integer:
            return int(appstruct.id)

    def deserialize(self, node, cstruct):
        """
        Deserialize takes input data from the request, validates it, and
        returns the deserialized value for this field, which in this case
        is the fetched model instance of the foreign key field.

        :param node: :class:`colander.SchemaNode`
        :param cstruct: Unvalidated object id
        :return: Model instance
        """
        value = self.field.deserialize(node, cstruct)

        # FIXME: we should possibly check if the self.pk is actually nullable
        # otherwise we might want to raise an Invalid exception here
        if value is colander.null:
            return None

        fk_obj = DBSession.query(self.model).get(value)

        # record was not found in db
        if fk_obj is None:
            raise colander.Invalid(node, '{} with id {} does not exist'.format(self.model.__name__, cstruct))

        return fk_obj


class Many2Many(DBField):
    """
    The purpose of the Many2Many colander field, is to take in a list
    of model id's as input and turn that into a list of model instances.

    Model objects are fetched from the database, to ensure the id's are valid.

    Model id's can be integer or string based.
    """

    def __init__(self, model, **kwargs):
        super().__init__(model)
        self.list_field = colander.List()

        if self.type in (String, Text):
            self.field = colander.String(**kwargs)
        elif self.type is Integer:
            self.field = colander.Integer()
        else:
            raise ValueError('Many2Many of type {} not supported'.format(self.type))

    def serialize(self, node, appstruct):
        """
        Serialize must do the opposite to deserialize, which is basically
        to return the list of model id's back.

        :param node: :class:`colander.SchemaNode`
        :param appstruct: List of model instances
        :return: List of model instance id's
        """
        if appstruct is colander.null:
            return appstruct

        if self.type in (String, Text):
            return [str(obj.id) for obj in appstruct]
        elif self.type is Integer:
            return [int(obj.id) for obj in appstruct]

    def deserialize(self, node, cstruct):
        """
        Deserialize should get a list of id's from the request, it should
        try to fetch all the objects to ensure they exist, then return
        a list of objects.

        :param node: :class:`colander.SchemaNode`
        :param cstruct: Unvalidated list of id's
        :return: List of model objects
        """
        # deserialize the list, so we don't have to validate that ourselves
        raw_ids = self.list_field.deserialize(node, cstruct)

        # list of id's should never contains a null item
        if None in raw_ids:
            raise colander.Invalid(node, "list of id's should not contain a null value")

        # loop and fetch each object, maybe we can do this in one query?
        ids = [self.field.deserialize(node, obj_id) for obj_id in raw_ids]

        # sqlalchemy generates a warning when using in_ with an empty lists
        if len(ids) > 0:
            # this will fetch all the objects in the m2m using a single query
            obj_list = list(DBSession.query(self.model).filter(self.model.id.in_(ids)))

            # not all the records in the m2m list exist
            actual_ids = {obj.id for obj in obj_list}
            missing = list(set(ids) - actual_ids)
            if missing:
                raise colander.Invalid(node, "{} objects with id {} do not exist".format(self.model.__name__, missing))

            return obj_list
        else:
            return []
