from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy,BaseQuery
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
"""
class MyQuery(BaseQuery):
    def SmartFilter(self, dicto):
        kwargs = {key:value for key,value in dicto.items() 
                  if value is not None}
        
        return self.filter_by(kwargs)
"""
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app) #query_class=MyQuery
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models
