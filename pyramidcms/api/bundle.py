class Bundle(object):
    """
    A small container for instances and converted data for the
    ``dehydrate/hydrate`` cycle.

    Necessary because the ``dehydrate/hydrate`` cycle needs to access data at
    different points.
    """

    def __init__(self, obj=None, data=None, request=None, resource=None):
        self.obj = obj
        self.data = data or {}
        self.request = request
        self.resource = resource

    def __repr__(self):
        return "<Bundle for obj: '{}' and with data: {}>".format(self.obj, self.data)

    def __json__(self, request):
        """
        This method is automatically called by Pyramid, if we are using
        the json renderer.

        :param request: Pyramid request object
        :return: dict that is safe to JSON serialize
        """
        return self.data
