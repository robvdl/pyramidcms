from pyramid.security import Allow, Authenticated


def groupfinder(username, request):
    """
    Returns groups for the given username, since we don't have different
    groups for users in the data model, just return an empty list.
    """
    return []


class RootFactory(object):
    """
    The RootFactory class is where to setup ACLs in the pyramid application,
    even though this is a url dispatch app instead of traversal.
    """
    __acl__ = [
        (Allow, Authenticated, 'admin')
    ]

    def __init__(self, request):
        self.request = request
