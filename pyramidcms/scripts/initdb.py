import os
import sys
import transaction

from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging
from pyramid.scripts.common import parse_vars

from pyramidcms.models import DBSession, Base
from pyramidcms.models.auth import User, Group, Permission


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: {} <config_uri> [var=value]\n'
          '(example: "{} development.ini")'.format(cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        # NOTE: this is mostly test data here for now and will be removed
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
