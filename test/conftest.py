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


import pytest
from app import init_app
from os.path import abspath as abspath
from os import environ as environ

@pytest.fixture(scope='module')
def test_client():
    app = init_app('test.cfg')
    app.testing = True
    app.config['Testing'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] =  abspath('test/test.db')
    app.config['SECRET_KEY'] = 'dev'
    app.config['EMAIL_PASS_PATH'] = 'Capstone1@'

    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

# https://gitlab.com/patkennedy79/flask_user_management_example/-/blob/main/tests/conftest.py#L12
# https://testdriven.io/blog/flask-pytest/ 