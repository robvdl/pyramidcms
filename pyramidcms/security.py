from pyramid.security import Allow, ALL_PERMISSIONS

from pyramidcms.models.auth import User, Permission


def groupfinder(username, request):
    """
    Pyramid auth framework callback that returns a list of groups (string)
    for the given username, often called "userid" in Pyramid.

    Note that username parameter is not used because we can already get to the
    User object from the request.user property which is lazy-loaded.
    """
    # this is the list of groups we return, this includes the
    # is_superuser and is_admin flags.
    groups = []

    # superuser implies admin as well, regardless if it's set or not
    if request.user.is_superuser:
        groups.extend(['is_superuser', 'is_admin'])
    elif request.user.is_admin:
        groups.append('is_admin')

    # Now the actual groups for this get added, we prefix groups with
    # "group:", just in case a group is actually called "is_superuser".
    groups.extend(['group:' + group.name for group in request.user.groups])

    return groups


def get_current_user(request):
    """
    Returns the current logged in User object.

    This gets added to the request object as the property "request.user",
    so it can be lazy-loaded by anything that requires it.

    Will return None if not currently logged in.
    """
    username = request.unauthenticated_userid
    if username is not None:
        return User.objects.get(username=username)


class RootFactory(object):
    """
    The RootFactory class is where we setup ACLs.

    It is also an entry point for traversal-based applications.
    """
    # The ACL table maps groups to Pyramid permission names
    # 'is_superuser' and 'is_admin' are not groups but flags on the User
    # Actual groups start with "group:" e.g. (Allow, 'group:Editors', 'edit')
    __acl__ = [
        (Allow, 'is_superuser', ALL_PERMISSIONS),
        (Allow, 'is_admin', 'admin')
    ]

    def __init__(self, request):
        self.request = request

        # This builds a list of custom permissions users may have
        # added to any Groups to the __acl__ table on each request.
        # FIXME: this is a place we should probably be doing some caching
        for permission, group in Permission.objects.list_by_group():
            self.__acl__.append((Allow, 'group:' + group.name, permission.codename))
