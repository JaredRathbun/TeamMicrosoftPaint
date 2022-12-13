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
import pytest
from app.models import RoleEnum

def __str_to_b64(str_to_convert: str):
    return b64encode(str_to_convert.encode('ascii')).decode('ascii')

@pytest.mark.parametrize('test_client', [[False]], indirect=True)
def test_get_login(test_client):
    res = test_client.get('/login')
    
    assert (res.status_code == 200)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_good_login(test_client):
    res = test_client.post('/login', content_type='application/json', json={
        'email': 'viewer@gmail.com', 
        'password': __str_to_b64('test123')
    }, follow_redirects=False)

    assert (res.status_code == 302)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


@pytest.mark.parametrize('test_client', [[False]], indirect=True)
def test_bad_login(test_client):
    res = test_client.post('/login', content_type='application/json', json={
        'email': 'dumy@dum4y.co', 
        'password': __str_to_b64('test')
    }, follow_redirects=False)

    assert (res.status_code == 401)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])


@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_good_admin_login(test_client):
    res = test_client.post('/login', json={
        'email': 'admin@gmail.com', 
        'password': __str_to_b64('test123')
    }, follow_redirects=False)

    assert (res.status_code == 302)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


@pytest.mark.parametrize('test_client', [[False]], indirect=True)
def test_merrimack_email_login(test_client):
    res = test_client.post('/login', json={
        'email': 'test@merrimack.edu', 
        'password': __str_to_b64('test123')
    });

    assert (res.status_code == 406)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])
    assert (b'{"message":"Cannot login with merrimack.edu email."}\n' 
        in res.data)


@pytest.mark.parametrize('test_client', [[False]], indirect=True)
def test_get_register(test_client):
    res = test_client.get('/register')

    assert (res.status_code == 200)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


@pytest.mark.parametrize('test_client', [[False]], indirect=True)
def test_good_register(test_client):
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


@pytest.mark.parametrize('test_client', [[False]], indirect=True)
def test_merrimack_email_register(test_client):
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


@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_existing_register(test_client):
    from app.models import User

    user_info = {
        'email': 'admin@gmail.com',
        'last_name': 'dummy',
        'first_name': 'user',
        'password': __str_to_b64('test123')
    }

    assert (User.query.get('admin@gmail.com'))

    res = test_client.post('/register', json=user_info)

    assert (res.status_code == 409)
    assert (b'{"message":"User exists"}\n' in res.data)


@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_bad_register_missing_first_name(test_client):
    user_info = {
        'email': 'dummy@dummy.com',
        'last_name': 'dummy',
        'password': __str_to_b64('test123')
    }

    res = test_client.post('/register', json=user_info)

    assert (res.status_code == 400)
    assert (b'{"message":"Invalid Request"}\n' in res.data)


@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_get_otp(test_client):
    res = test_client.get('/otp/admin@gmail.com')

    assert (res.status_code == 200)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_get_otp_not_admin(test_client):
    res = test_client.get('/otp/viewer@gmail.com')

    assert (res.status_code == 403)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])
    assert (b'{"message":"User is not an admin."}\n' in res.data)


@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_good_otp_auth(test_client):
    from app.models import User

    usr = User.query.get('admin@gmail.com')
    otp = usr.get_otp()

    res = test_client.post('/otp/admin@gmail.com', json={
        'otp': otp
    }, follow_redirects=False)

    assert (res.status_code == 302)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_bad_otp_auth(test_client):
    otp = 123456

    res = test_client.post('/otp/admin@merrimack.edu', json={
        'otp': otp
    }, follow_redirects=False)

    assert (res.status_code == 401)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])
    assert (b'{"message":"Invalid OTP Code"}\n' == res.data)


@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_otp_auth_bad_body(test_client):
    res = test_client.post('/otp/admin@gmail.com', json={

    }, follow_redirects=False)

    assert (res.status_code == 400)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])
    assert (b'{"message":"Invalid request."}\n' == res.data)


@pytest.mark.parametrize('test_client', [[False]], indirect=True)
def test_get_reset(test_client):
    res = test_client.get('/reset')

    assert (res.status_code == 200)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


@pytest.mark.parametrize('test_client', [[False]], indirect=True)
def test_get_sendreset(test_client):
    res = test_client.get('/sendreset')

    assert (res.status_code == 200)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_post_good_sendreset(test_client):
    res = test_client.post('/sendreset', json={
        'email': 'admin@gmail.com'
    })

    assert (res.status_code == 200)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])
    assert (b'{"message":"Success"}\n' == res.data)
    

@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_post_bad_sendreset(test_client):
    res = test_client.post('/sendreset', json={
        'email': 'admin.teammspaint@gmail.c'
    })

    assert (res.status_code == 400)


@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_reset_password_good(test_client):
    from app.models import User

    usr = User.query.get('admin@gmail.com')
    reset_token = usr.get_reset_token()

    reset_body = {
        'token': reset_token,
        'password': __str_to_b64('test1234')
    }

    res = test_client.post('/reset', json=reset_body, follow_redirects=False)

    assert (res.status_code == 302)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])


@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_reset_with_old_password(test_client):
    from app.models import User

    from app.models import User

    usr = User.query.get('admin@gmail.com')
    reset_token = usr.get_reset_token()

    # The password is changed to 'test1234' in the test above.
    reset_body = {
        'token': reset_token,
        'password': __str_to_b64('test123')
    }

    res = test_client.post('/reset', json=reset_body, follow_redirects=False)

    assert (res.status_code == 409)
    assert ('Content-Type' in res.headers)
    assert ('application/json' == res.headers['Content-Type'])
    assert (b'' in res.data)


@pytest.mark.parametrize('test_client', [[True]], indirect=True)
def test_logout(test_client):
    res = test_client.post('/logout', follow_redirects=False)

    assert (res.status_code == 302)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])