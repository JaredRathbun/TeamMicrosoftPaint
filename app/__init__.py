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
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from functools import wraps
from flask import Flask
from os import environ
from flask_session import Session
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path, environ
import logging as logger
from flask_mail import Mail
from flask_login import current_user


app = Flask('STEM Data Dashboard', instance_relative_config=True,
    template_folder=path.abspath('./app/templates'),
    static_folder=path.abspath('./app/static')
)

env = environ['env']
if (env not in ('dev', 'prod')):
    logger.critical("Invalid environment. Please use either 'dev' or 'prod'.")
    raise SystemExit()
else:
    config_loaded = app.config.from_pyfile(f'{env}.cfg')

    if (not config_loaded):
        logger.critical('Failed to load configuration and start correctly.')
        raise SystemExit('Failed to load configuration and start correctly.')

db = SQLAlchemy(app)
jwt_manager = JWTManager()
mail = Mail()
login_manager = LoginManager(app)
login_manager.login_view = 'routes.login'

def init_app() -> Flask:
    # Blueprints need to be registered here.
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.dashboard.routes import dash_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)
    
    # Init the DB, create all tables.
    with app.app_context():
        db.init_app(app)
        # from app.models import User, Student, ClassData
        db.create_all()

    jwt_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Set up the SMTP connection for Gmail.
    mail.init_app(app)

    return app
    

def admin_required(f):
    @wraps(f)
    def dec_func(*args, **kwargs):
        from app.models import RoleEnum
        if current_user.role == RoleEnum.ADMIN:
            return f(*args, **kwargs)
        else:
            return {'message': 'User is not an admin.'}, 401
    return dec_func


def data_admin_or_higher_required(f):
    @wraps(f)
    def dec_func(*args, **kwargs):
        from app.models import RoleEnum
        if (current_user.role == RoleEnum.DATA_ADMIN or 
            current_user.role == RoleEnum.ADMIN):
            return f(*args, **kwargs)
        else:
            return {'message': 'User is not a data admin.'}, 401
    return dec_func


def is_data_admin_or_higher(current_u):
    from app.models import RoleEnum
    '''
    Returns whether or not the user is a data admin or higher role.

    param:
        `current_u`: The current user represented in a `User` object.
    return: 
        A `bool` representing if the user is a data_admin or a higher role.
    '''
    return (current_u.role == RoleEnum.DATA_ADMIN or current_u.role == RoleEnum.ADMIN)


def is_admin(current_u):
    from app.models import RoleEnum
    '''
    Returns whether or not the user is an admin role.

    param:
        `current_u`: The current user represented in a `User` object.
    return: 
        A `bool` representing if the user is an admin or not.
    '''
    return (current_u.role == RoleEnum.ADMIN)


@app.context_processor
def utility_functions():
    '''
    Utility functions used with the Jinja templating engine.
    '''
    def print_in_console(message):
        '''
        Prints the given message to the console.

        param:
            `message`: The message to print.
        '''
        print(str(message))

    return dict(print_debug=print_in_console)

app.jinja_env.globals.update(is_data_admin_or_higher=is_data_admin_or_higher)
app.jinja_env.globals.update(is_admin=is_admin)