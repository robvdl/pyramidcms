class Bundle(object):
    """
    A small container for instances and converted data for the
    ``dehydrate/hydrate`` cycle.

    Necessary because the ``dehydrate/hydrate`` cycle needs to access data at
    different points.
    """

    def __init__(self, obj=None, data=None, request=None, resource=None, items=None, meta=None):
        self.obj = obj
        self.data = data or {}
        self.request = request
        self.resource = resource
        self.items = items or []
        self.meta = meta or {}

    def __repr__(self):
        if self.obj is not None:
            return "<Bundle for obj: '{}' and with data: {}>".format(self.obj, self.data)
        else:
            return "<Bundle with items: {}>".format(self.items)

    def __json__(self, request):
        """
        This method is automatically called by Pyramid, if we are using
        the json renderer.

        :param request: Pyramid request object
        :return: dict that is safe to JSON serialize
        """
        if self.obj is not None:
            return self.data
        else:
            return {
                'meta': self.meta,
                'items': [item.__json__(self.request) for item in self.items]
            }
