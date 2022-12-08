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
#
# Code referenced from: 
# https://gitlab.com/patkennedy79/flask_user_management_example/-/blob/main/tests/conftest.py#L12
# https://testdriven.io/blog/flask-pytest/

# Add the directory above the tests/ directory to the sys path so the app can
# be imported.
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from app import init_app, db
from os.path import abspath as abspath
from os import environ as environ
from sqlalchemy.orm import declarative_base
from base64 import b64encode 

def __str_to_b64(str_to_convert: str):
    return b64encode(str_to_convert.encode('ascii')).decode('ascii')


@pytest.fixture(scope='module')
def test_client():
    app = init_app()
    app.config.from_pyfile('test.cfg')
    app.testing = True
    app.config['DEBUG'] = False
    app.config['SECRET_KEY'] = 'dev'

    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client
            db.drop_all()


@pytest.fixture(scope='module')
def init_db():
    base = declarative_base()

    from app.models import User
    
    db.create_all()
    
    # base.metadata.drop_all(bind=db.engine)
    # base.metadata.create_all(bind=db.engine)
    local_usr = User('dummy@dummy.com', 'dummy', 'user', 'test123')
    google_usr = User('dummy@gmail.com', 'dummy', 'googleuser')
    admin_usr = User('admin.teammspaint@gmail.com', 'dummy', 'admin', 'test123')
    admin_usr.set_admin()

    User.insert_user(local_usr)
    User.insert_user(google_usr)
    User.insert_user(admin_usr)

    db.session.commit()

    yield

    db.session.close()
    # base.metadata.drop_all(bind=db.engine)
    db.drop_all()