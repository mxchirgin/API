#!flask/bin/python
import datetime
import imp
from migrate.versioning import api
import sys
sys.path.append('C:\\Users\\maxch\\AppData\\Local\\Programs\\Python\\Python38\\REST API')
import os
from app import db

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join('C:\\Users\\maxch\\AppData\\Local\\Programs\\Python\\Python38\\REST API', 'api.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join('C:\\Users\\maxch\\AppData\\Local\\Programs\\Python\\Python38\\REST API', 'db_repository')
migration = SQLALCHEMY_MIGRATE_REPO + '/versions/%03d_migration.py' % (api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO) + 1)
tmp_module = imp.new_module('old_model')
old_model = api.create_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
exec (old_model, tmp_module.__dict__)
script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, db.metadata)
open(migration, "wt").write(script)
api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
print ('New migration saved as ', migration)
print ('Current database version: ' , str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)))
