#!flask/bin/python
from migrate.versioning import api
import sys
import pathlib
p =pathlib.Path(__file__).parent.parent.absolute()

sys.path.append(str(p))
from app import db
import os.path
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(str(p), 'api.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(str(p), 'db_repository')

db.create_all()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))
