import transaction

from pyramidcms.cli import BaseCommand
from pyramidcms.models import User, Group, Permission


class Command(BaseCommand):
    """
    For now this just installs some test data.

    Later this will load generic JSON fixtures.
    """

    def handle(self, args):
        with transaction.manager:
            # permissions
            perms = {}

            # load some permissions for the API resource ACLAuthorization class
            for resource in ('user', 'group', 'permission'):
                perms[resource] = {
                    'create': Permission.objects.create(
                        name='create-' + resource,
                        description='User can create {} resources.'.format(resource)
                    ),
                    'read': Permission.objects.create(
                        name='read-' + resource,
                        description='User can read {} resources.'.format(resource)
                    ),
                    'update': Permission.objects.create(
                        name='update-' + resource,
                        description='User can update {} resources.'.format(resource)
                    ),
                    'delete': Permission.objects.create(
                        name='delete-' + resource,
                        description='User can delete {} resources.'.format(resource)
                    ),
                }

            # groups
            g1 = Group.objects.create(name='Group 1', permissions=[
                perms['user']['create'],
                perms['user']['read'],
                perms['user']['update'],
                perms['user']['delete'],
            ])
            g2 = Group.objects.create(name='Group 2', permissions=[
                perms['group']['create'],
                perms['group']['read'],
                perms['group']['update'],
                perms['group']['delete'],
            ])
            g3 = Group.objects.create(name='Group 3', permissions=[
                perms['permission']['create'],
                perms['permission']['read'],
                perms['permission']['update'],
                perms['permission']['delete'],
            ])

            # users
            admin_user = User(username='admin', is_superuser=True, groups=[g1, g2])
            admin_user.set_password('admin')
            admin_user.save()
            test_user = User(username='test', groups=[g1, g3])
            test_user.set_password('test')
            test_user.save()
