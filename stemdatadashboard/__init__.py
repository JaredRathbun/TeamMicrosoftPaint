from flask import Flask
from os import environ
from flask_session import Session
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from stemdatadashboard.blueprints import auth

app = Flask('STEM Data Dashboard', template_folder='templates')
db = SQLAlchemy()
jwt_manager = JWTManager()
session = Session()
login_manager = LoginManager(app)
login_manager.login_view = 'routes.login'

def init_app() -> Flask:
    # Based on the 'INSTANCE_MODE' environment variable, set the correct config
    env = environ.get('ENV')

    if env == 'dev':
        app.config.from_object('config.DevConfig')
    else:
        app.config.from_object('config.ProdConfig')

    # Blueprints need to be registered here.

    
    # Init the DB, create all tables.
    db.init_app(app)
    with app.app_context():
        db.create_all()

    jwt_manager.init_app(app)
    session.init_app(app)
    login_manager.init_app(app)

    from stemdatadashboard.blueprints.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    return app
    