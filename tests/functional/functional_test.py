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


from base64 import b64encode 
import pandas as pd
from io import BytesIO
from os import path
import json


def __str_to_b64(str_to_convert: str):
    return b64encode(str_to_convert.encode('ascii')).decode('ascii')


def test_get_login(test_client):
    res = test_client.get('/login')
    
    assert (res.status_code == 200)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


def test_good_login(test_client, init_db):
    res = test_client.post('/login', content_type='application/json', json={
        'email': 'dummy@dummy.com', 
        'password': __str_to_b64('test123')
    }, follow_redirects=False)

    assert (res.status_code == 302)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


def test_bad_login(test_client, init_db):
    res = test_client.post('/login', content_type='application/json', json={
        'email': 'dumy@dum4y.co', 
        'password': __str_to_b64('test')
    }, follow_redirects=False)

    assert (res.status_code == 401)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])


def test_good_admin_login(test_client, init_db):
    res = test_client.post('/login', json={
        'email': 'admin.teammspaint@gmail.com', 
        'password': __str_to_b64('test123')
    }, follow_redirects=False)

    assert (res.status_code == 302)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


def test_merrimack_email_login(test_client, init_db):
    res = test_client.post('/login', json={
        'email': 'test@merrimack.edu', 
        'password': __str_to_b64('test123')
    });

    assert (res.status_code == 406)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])
    assert (b'{"message":"Cannot login with merrimack.edu email."}\n' 
        in res.data)

    
def test_get_register(test_client):
    res = test_client.get('/register')

    assert (res.status_code == 200)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


def test_good_register(test_client, init_db):
    user_info = {
        'email': 'test@tester.com',
        'last_name': 'Tester',
        'first_name': 'Test',
        'password': __str_to_b64('test123')
    }

    res = test_client.post('/register', json=user_info, follow_redirects=False)

    assert (res.status_code == 302)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])

    from app.models import User
    assert (User.query.get('test@tester.com'))


def test_merrimack_email_register(test_client, init_db):
    user_info = {
        'email': 'dummy@merrimack.edu',
        'last_name': 'dummy',
        'first_name': 'user',
        'password': __str_to_b64('test123')
    }

    res = test_client.post('/register', json=user_info)

    assert (res.status_code == 406)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])
    assert (b'{"message":"User has merrimack.edu email."}\n' in res.data)


def test_existing_register(test_client, init_db):
    from app.models import User

    user_info = {
        'email': 'dummy@dummy.com',
        'last_name': 'dummy',
        'first_name': 'user',
        'password': __str_to_b64('test123')
    }

    assert (User.query.get('dummy@dummy.com'))

    res = test_client.post('/register', json=user_info)

    assert (res.status_code == 409)
    assert (b'{"message":"User exists"}\n' in res.data)


def test_bad_register_missing_first_name(test_client, init_db):
    user_info = {
        'email': 'dummy@dummy.com',
        'last_name': 'dummy',
        'password': __str_to_b64('test123')
    }

    res = test_client.post('/register', json=user_info)

    assert (res.status_code == 400)
    assert (b'{"message":"Invalid Request"}\n' in res.data)


def test_get_otp(test_client, init_db):
    res = test_client.get('/otp/admin.teammspaint@gmail.com')

    assert (res.status_code == 200)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


def test_get_otp_not_admin(test_client, init_db):
    res = test_client.get('/otp/dummy@dummy.com')

    assert (res.status_code == 403)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])
    assert (b'{"message":"User is not an admin."}\n' in res.data)


def test_good_otp_auth(test_client, init_db):
    from app.models import User

    usr = User.query.get('admin.teammspaint@gmail.com')
    otp = usr.get_otp().now()

    res = test_client.post('/otp/admin.teammspaint@gmail.com', json={
        'otp': otp
    }, follow_redirects=False)

    assert (res.status_code == 302)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


def test_bad_otp_auth(test_client):
    otp = 123456

    res = test_client.post('/otp/admin.teammspaint@gmail.com', json={
        'otp': otp
    }, follow_redirects=False)

    assert (res.status_code == 401)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])
    assert (b'{"message":"Invalid OTP Code"}\n' == res.data)


def test_otp_auth_bad_body(test_client):
    res = test_client.post('/otp/admin.teammspaint@gmail.com', json={

    }, follow_redirects=False)

    assert (res.status_code == 400)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])
    assert (b'{"message":"Invalid request."}\n' == res.data)


def test_get_reset(test_client):
    res = test_client.get('/reset')

    assert (res.status_code == 200)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


def test_get_sendreset(test_client):
    res = test_client.get('/sendreset')

    assert (res.status_code == 200)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


def test_post_good_sendreset(test_client, init_db):
    from app.models import User

    res = test_client.post('/sendreset', json={
        'email': 'admin.teammspaint@gmail.com'
    })

    assert (res.status_code == 200)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])
    assert (b'{"message":"Success"}\n' == res.data)
    


def test_post_bad_sendreset(test_client, init_db):
    res = test_client.post('/sendreset', json={
        'email': 'admin.teammspaint@gmail.c'
    })

    assert (res.status_code == 400)


def test_reset_password_good(test_client, init_db):
    from app.models import User

    usr = User.query.get('admin.teammspaint@gmail.com')
    reset_token = usr.get_reset_token()

    reset_body = {
        'token': reset_token,
        'password': __str_to_b64('test1234')
    }

    res = test_client.post('/reset', json=reset_body, follow_redirects=False)

    assert (res.status_code == 302)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


def test_reset_with_old_password(test_client, init_db):
    from app.models import User

    from app.models import User

    usr = User.query.get('admin.teammspaint@gmail.com')
    reset_token = usr.get_reset_token()

    # The password is changed to 'test1234' in the test above.
    reset_body = {
        'token': reset_token,
        'password': __str_to_b64('test1234')
    }

    res = test_client.post('/reset', json=reset_body, follow_redirects=False)

    assert (res.status_code == 409)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])
    assert (b'' in res.data)


def test_logout(test_client):
    res = test_client.post('/logout', follow_redirects=False)

    assert (res.status_code == 302)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


def __read_file(file_name: str) -> tuple[BytesIO, str]:
    '''
    Reads the file at the specified file, and returns a tuple containing the 
    bytes of the object wrapped in a BytesIO object, and the file path.

    param:
        file_name: The name of the file.
    return:
        A tuple containing (BytesIO, file path)
    '''
    file_path = path.normpath(path.dirname(__file__) + f'/test_data/{file_name}')
    
    with open(file_path, 'rb') as file:
        return (BytesIO(file.read()), file_path)


def test_good_data_upload(test_client):
    from app.models import Student, Course, ClassData
    
    file = {
        'file': __read_file('good_test_data.csv')
    }
    res = test_client.post('/upload', data=file)

    assert (res.status_code == 200)
    
    # There should be 13 students in the database.
    assert (len(Student.query.all()) == 13)

    # There should be 6 Courses.
    assert (len(Course.query.all()) == 6)

    # There should be 15 ClassData objects.
    assert(len(ClassData.query.all()) == 15)
    


def test_bad_data_upload(test_client, init_db):
    from app.models import Student, ClassData, Course
    from app import db

    # Clear the database.
    Student.query.delete()
    ClassData.query.delete()
    Course.query.delete()

    file = {
        'file': __read_file('bad_test_data.csv')
    }

    res = test_client.post('/upload', data=file)

    '''
    The test file for this test has a bad leave date, first gen student, and 
    SAT score. 
    '''
    
    dict_res = json.loads(res.data.decode('utf-8'))
    assert (res.status_code == 400)
    # Missing admit type, program_level is incorrect, major1_desc missing, 
    # course ID missing, term incorrect.
    assert (len(dict_res['errors']) == 6)
    assert (dict_res['message'] == 'Errors while parsing data.')