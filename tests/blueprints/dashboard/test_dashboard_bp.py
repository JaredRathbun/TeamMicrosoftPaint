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

# NOTE: THESE TESTS ARE NOT WORKING AS A SOLUTION FOR MOCKING A LOGGED IN USER
# HAS NOT BEEN FOUND YET.
from app.models import RoleEnum
import pytest


@pytest.mark.parametrize('test_client', [[True, RoleEnum.VIEWER, True]], 
    indirect=True)
def test_get_dashboard(test_client):
    res = test_client.get('/dashboard')
    
    assert (res.status_code == 200)
    assert ('Content-Type' in res.headers)
    assert ('text/html; charset=utf-8' == res.headers['Content-Type'])

    
# def __read_file(file_name: str) -> tuple[BytesIO, str]:
#     '''
#     Reads the file at the specified file, and returns a tuple containing the 
#     bytes of the object wrapped in a BytesIO object, and the file path.

#     param:
#         file_name: The name of the file.
#     return:
#         A tuple containing (BytesIO, file path)
#     '''
#     file_path = path.normpath(path.dirname(__file__) + f'/test_data/{file_name}')
    
#     with open(file_path, 'rb') as file:
#         return (BytesIO(file.read()), file_path)


# def test_good_data_upload(test_client):
#     from app.models import Student, Course, ClassData
    
#     file = {
#         'file': __read_file('good_test_data.csv')
#     }
#     res = test_client.post('/upload', data=file)

#     assert (res.status_code == 200)
    
#     # There should be 13 students in the database.
#     assert (len(Student.query.all()) == 13)

#     # There should be 6 Courses.
#     assert (len(Course.query.all()) == 6)

#     # There should be 15 ClassData objects.
#     assert(len(ClassData.query.all()) == 15)
    

# @pytest.mark.parametrize('test_client', [[RoleEnum.ADMIN, True]], indirect=True)
# def test_bad_data_upload(test_client):
#     from app.models import Student, ClassData, Course
#     from app import db

#     # Clear the database.
#     Student.query.delete()
#     ClassData.query.delete()
#     Course.query.delete()

#     file = {
#         'file': __read_file('bad_test_data.csv')
#     }

#     res = test_client.post('/upload', data=file)

#     '''
#     The test file for this test has a bad leave date, first gen student, and 
#     SAT score. 
#     '''
    
#     dict_res = json.loads(res.data.decode('utf-8'))
#     assert (res.status_code == 400)
#     # Missing admit type, program_level is incorrect, major1_desc missing, 
#     # course ID missing, term incorrect.
#     assert (len(dict_res['errors']) == 6)
#     assert (dict_res['message'] == 'Errors while parsing data.')