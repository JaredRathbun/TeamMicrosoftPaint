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


from base64 import b64encode


def __str_to_b64(str_to_convert: str):
    return b64encode(str_to_convert.encode('ascii')).decode('ascii')

def test_get_login(test_client):
    res = test_client.get('/login')
    
    assert (res.status_code == 200)


def test_good_login(test_client, init_db):
    res = test_client.post('/login', content_type='application/json', json={
        'email': 'dummy@dummy.com', 
        'password': __str_to_b64('test123')
    }, follow_redirects=False)

    assert (res.status_code == 302)
