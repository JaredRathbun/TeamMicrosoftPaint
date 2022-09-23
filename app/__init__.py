from flask import Flask
from os import environ
from flask_session import Session
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path


app = Flask('STEM Data Dashboard', 
    template_folder=path.abspath('../app/templates/'),
    static_folder=path.abspath('../app/static/')
)
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
    from app.blueprints.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    
    # Init the DB, create all tables.
    db.init_app(app)
    with app.app_context():
        db.create_all()

    jwt_manager.init_app(app)
    session.init_app(app)
    login_manager.init_app(app)

    return app
    