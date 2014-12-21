import os
import sys
import transaction

from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging
from pyramid.scripts.common import parse_vars

from pyramidcms.models import DBSession, Base
from pyramidcms.models.auth import User


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
        admin_user = User(username='admin', superuser=True)
        admin_user.set_password('admin')
        DBSession.add(admin_user)
