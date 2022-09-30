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
# Code referenced from: 
# https://gitlab.com/patkennedy79/flask_user_management_example/-/blob/main/tests/conftest.py#L12
# https://testdriven.io/blog/flask-pytest/

from cgi import test
import pytest
from app import init_app, db, app
from os.path import abspath as abspath
from os import environ as environ
from sqlalchemy.orm import declarative_base

@pytest.fixture(scope='module')
def test_client():
    app = init_app('test.cfg')
    app.testing = True
    app.config['SECRET_KEY'] = 'dev'

    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client


@pytest.fixture(scope='module')
def init_db(test_client):
    base = declarative_base()

    from app.models import User
    
    base.metadata.drop_all(db.engine)
    base.metadata.create_all(db.engine)
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
    base.metadata.drop_all(bind=db.engine)
    db.drop_all()
 