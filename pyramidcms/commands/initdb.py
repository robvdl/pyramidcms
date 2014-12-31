import transaction

from pyramidcms.cli import BaseCommand
from pyramidcms.models import Base, DBSession
from pyramidcms.models.auth import User, Group, Permission


class Command(BaseCommand):
    """
    Command that creates the database tables and loads some test data,
    note that this is intended to be replaced by Alembic later.
    """

    def handle(self, args):
        Base.metadata.create_all(DBSession.bind)
        with transaction.manager:
            perm_create = Permission.objects.create(codename='create', name='User can create item')
            perm_edit = Permission.objects.create(codename='edit', name='User can edit content')
            perm_delete = Permission.objects.create(codename='delete', name='User can delete items')
            perm_view = Permission.objects.create(codename='view', name='User can view item')
            g1 = Group.objects.create(name='Group 1', permissions=[perm_create])
            g2 = Group.objects.create(name='Group 2', permissions=[perm_delete, perm_create, perm_view])
            g3 = Group.objects.create(name='Group 3', permissions=[perm_create, perm_edit])
            admin_user = User(username='admin', is_superuser=True, is_admin=True, groups=[g1, g2])
            admin_user.set_password('admin')
            admin_user.save()
            test_user = User(username='test', groups=[g1, g3])
            test_user.set_password('test')
            test_user.save()
