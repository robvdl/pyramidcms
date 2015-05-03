import os
import binascii

from pyramid.security import Allow, ALL_PERMISSIONS

from pyramidcms.models import User, Permission


def groupfinder(username, request):
    """
    Pyramid auth framework callback that returns a list of groups (strings)
    for the given username, often called "userid" in Pyramid.

    Note that username parameter is not used because we can already get to the
    User object from the request.user property which is lazy-loaded.
    """
    # groups start with "group:" in case a group is called "superuser"
    groups = ['group:' + group.name for group in request.user.groups]

    # treat the is_superuser bool as a group, then in the RootFactory
    # ACL we give this ALL_PERMISSIONS.
    if request.user.is_superuser:
        groups.append('superuser')

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


def secret_key_generator(length):
    """
    Generate a new secret key using length given.
    """
    return binascii.hexlify(os.urandom(length)).decode('utf-8')


class RootFactory(object):
    """
    The RootFactory class is where we setup ACLs.

    It is also an entry point for traversal-based applications.
    """
    __acl__ = [(Allow, 'superuser', ALL_PERMISSIONS)]

    def __init__(self, request):
        """
        The RootFactory constructor runs for every request so we don't
        want to do too much work here.

        Since we have permissions stored on groups in the database, we
        build a list of ACLs based on a join between Group and Permission.

        TODO: this is a place where we could possibly do some caching.

        :param request: Pyramid request object
        """
        self.request = request

        # add ACLs from database based on a join between Group and Permission
        acl = [(Allow, 'group:' + grp.name, perm.name) for perm, grp in Permission.objects.list_by_group()]
        self.__acl__.extend(acl)
