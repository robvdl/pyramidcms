import transaction

from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging

from pyramidcms.cli import BaseCommand
from pyramidcms.models import DBSession, Base
from pyramidcms.models.auth import User, Group, Permission


class Command(BaseCommand):
    """
    Command that creates the database tables and loads some test data,
    note that this is intended to be replaced by Alembic later.
    """

    def setup_args(self, parser):
        parser.add_argument('config_file', type=str,
            help='Location of the pyramidcms.ini config file')

    def handle(self, args):
        setup_logging(args.config_file)
        settings = get_appsettings(args.config_file, options={})
        engine = engine_from_config(settings, 'sqlalchemy.')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

        # NOTE: this is mostly test data here for now and will be removed
        with transaction.manager:
            perm_create = Permission.objects.create(codename='create', name='User can create item')
            perm_edit = Permission.objects.create(codename='edit', name='User can edit content')
            perm_delete = Permission.objects.create(codename='delete', name='User can delete items')
            perm_view = Permission.objects.create(codename='view', name='User can view item')
            g1 = Group.objects.create(name='Group 1', permissions=[perm_create])
            g2 = Group.objects.create(name='Group 2', permissions=[perm_delete, perm_create, perm_view])
            g3 = Group.objects.create(name='Group 3', permissions=[perm_create, perm_edit])
            admin_user = User(username='admin', is_superuser=True, is_admin=True)
            admin_user.set_password('admin')
            admin_user.groups.append(g1)
            admin_user.groups.append(g2)
            admin_user.save()
            test_user = User(username='test')
            test_user.set_password('test')
            test_user.groups.extend([g1, g3])
            test_user.save()
