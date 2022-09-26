# Copyright (c) 2022 Jared Rathbun and Katie O'Neil. 
#
# This file is part of STEM Data Dashboard.
# 
# STEM Data Dashboard is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free 
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# STEM Data Dashboard is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more 
# details.
#
# You should have received a copy of the GNU General Public License along with 
# STEM Data Dashboard. If not, see <https://www.gnu.org/licenses/>.


from flask import Flask
from os import environ
from flask_session import Session
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
import logging as logger

app = Flask('STEM Data Dashboard', instance_relative_config=True,
    template_folder=path.abspath('./app/templates'),
    static_folder=path.abspath('./app/static')
)

db = SQLAlchemy(app)
jwt_manager = JWTManager()
session = Session()
login_manager = LoginManager(app)
login_manager.login_view = 'routes.login'

def init_app(config_fname: str = None) -> Flask:
    config_loaded = app.config.from_pyfile(config_fname)
    if config_loaded:
        # Blueprints need to be registered here.
        from app.blueprints.auth.routes import auth_bp
        app.register_blueprint(auth_bp)
        
        # Init the DB, create all tables.
        with app.app_context():
            db.init_app(app)
            from app.models import User, Student, MCASScore, ClassData
            db.create_all()


        jwt_manager.init_app(app)
        session.init_app(app)
        login_manager.init_app(app)

        return app
    else:
        logger.critical('Failed to load config file. Please make sure it exists in the /config directory.')
        raise SystemExit()
    