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
from app.models import RoleEnum, User

app = init_app()
app.testing = True
app.config['TESTING'] = True
app.config['LOGIN_DISABLED'] = True
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = 'testingkey'
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False


@pytest.fixture
def test_client(request, mocker):
    fill_data = request.param[0]

    user_role, use_google = None, None
    if (len(request.param) > 1):
        user_role = request.param[1]
        use_google = request.param[2]

    with app.test_client() as test_client:
        app_context = app.app_context()
        with app_context:

            def __apply_role(user: User, role: RoleEnum) -> User:
                assert (user is not None) and (role in 
                    (RoleEnum.DATA_ADMIN, RoleEnum.ADMIN))

                match role:
                    case RoleEnum.DATA_ADMIN:
                        user.set_data_admin()
                    case RoleEnum.ADMIN:
                        user.set_admin()
                return user

            db.create_all()
            if (fill_data):
                '''
                Local and Google users with the Viewer role.
                '''
                LOCAL_VIEWER = User('viewer@gmail.com', 'Test', 'Viewer', 
                    'test123')
                GOOGLE_VIEWER = User('viewer@merrimack.edu', 'Test', 'Viewer')
                
                '''
                Local and Google users with the Data Admin Role.
                '''
                LOCAL_DATA_ADMIN = __apply_role(
                    User('data_admin@gmail.com', 'Test', 'DataAdmin', 'test123'), 
                    RoleEnum.DATA_ADMIN)
                GOOGLE_DATA_ADMIN = __apply_role(
                    User('data_admin@merrimack.edu', 'Test', 'DataAdmin'), 
                        RoleEnum.DATA_ADMIN)

                '''
                Local and Google users with the Admin Role.
                '''
                LOCAL_ADMIN = __apply_role(
                    User('admin@gmail.com', 'Test', 'Admin', 'test123'), 
                        RoleEnum.ADMIN)
                GOOGLE_ADMIN = __apply_role(
                    User('admin@merrimack.edu', 'Test', 'Admin'), 
                        RoleEnum.ADMIN)

                User.insert_user(LOCAL_VIEWER)
                User.insert_user(GOOGLE_VIEWER)
                User.insert_user(LOCAL_DATA_ADMIN)
                User.insert_user(GOOGLE_DATA_ADMIN)
                User.insert_user(LOCAL_ADMIN)
                User.insert_user(GOOGLE_ADMIN)
                db.session.commit()

                if (user_role is not None and use_google is not None):
                    match user_role:
                        case RoleEnum.VIEWER:
                            mock_user = GOOGLE_VIEWER if (use_google) else LOCAL_VIEWER
                        case RoleEnum.DATA_ADMIN:
                            mock_user = GOOGLE_DATA_ADMIN if (use_google) else LOCAL_DATA_ADMIN
                        case RoleEnum.ADMIN:
                            mock_user = GOOGLE_ADMIN if (use_google) else LOCAL_ADMIN
                    mocker.patch('flask_login.current_user', mock_user)
                
            yield test_client
            db.session.close()
            db.drop_all()