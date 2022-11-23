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


from . import dash_bp
from flask import render_template, request, make_response
from flask_login import login_required, current_user
from app import admin_required, data_admin_or_higher_required
from app.blueprints.dashboard.data_upload import upload_csv_file
from app.models import RoleEnum, User, ClassData, Course, Student, Utils
import pandas as pd

@dash_bp.route('/dashboard', methods = ['GET'])
@login_required
def get_dash():
    name = current_user.first_name + ' ' + current_user.last_name
    dwf_avg = ClassData.get_avg_dwf()
    avg_gpa = Student.get_avg_gpa()
    avg_course_grade = ClassData.get_avg_grade()
    total_students = len(Student.query.all())
    num_students_per_major = Student.get_num_students_per_major()
    
    return render_template('dashboard/dashboard.html', current_user=current_user,
        user_name=name, dwf_avg=dwf_avg, avg_gpa=avg_gpa, 
        avg_course_grade=avg_course_grade, total_students=total_students,
        num_students_per_major=num_students_per_major)


@dash_bp.route('/data', methods = ['GET'])
@login_required
def get_data():
    name = current_user.first_name + ' ' + current_user.last_name
    return render_template('dashboard/data.html', current_user=current_user,
        user_name=name)


@dash_bp.route('/visualizations', methods = ['GET'])
@login_required
def get_visualizations():
    name = current_user.first_name + ' ' + current_user.last_name
    dwf_avg = ClassData.get_avg_dwf()
    avg_gpa = Student.get_avg_gpa()
    avg_course_grade = ClassData.get_avg_grade()
    total_students = len(Student.query.all())
    lowest_highest_years = Course.get_highest_lowest_years()
    avg_high_school_gpa = Student.get_avg_high_school_gpa()
    avg_math_placement = Student.get_avg_math_placement()
    avg_sat_total = Student.get_avg_sat_total()
    avg_sat_math = Student.get_avg_sat_math()
    avg_act_score = Student.get_avg_act()
    return render_template('dashboard/visualizations.html', 
        current_user=current_user, user_name=name, dwf_avg=dwf_avg, 
        avg_gpa=avg_gpa, avg_course_grade=avg_course_grade, 
        total_students=total_students, lowest_highest_years = lowest_highest_years,
        avg_high_school_gpa = avg_high_school_gpa, avg_math_placement = avg_math_placement,
        avg_sat_total = avg_sat_total, avg_sat_math = avg_sat_math,
        avg_act_score = avg_act_score)


@dash_bp.route('/dataadmin', methods = ['GET'])
@login_required
@data_admin_or_higher_required
def get_data_admin():
    name = current_user.first_name + ' ' + current_user.last_name
    
    user_query = User.query
    total_admins = len(user_query.filter_by(role=RoleEnum.ADMIN).all())
    total_users = len(user_query.all())
    total_students = len(Student.query.all())
    total_data_admins = len(User.query.filter(User.role==RoleEnum.DATA_ADMIN).all())
    
    return render_template('dashboard/dataadmin.html', current_user=current_user, 
            user_name=name, total_admins=total_admins, total_users=total_users,
            total_students=total_students, total_data_admins=total_data_admins)

@dash_bp.route('/admin', methods = ['GET'])
@login_required
@admin_required
def get_admin():
    def get_user_dict(u: User) -> str:
        '''
        Returns a `str` representation of whether or not the user is admin.
        '''
        if u:
            if (u.role == RoleEnum.ADMIN):
                role = 'Admin'
            elif (u.role == RoleEnum.DATA_ADMIN):
                role = 'Data Admin'
            else:
                role = 'Viewer'

            return {
                'name': u.first_name + ' ' + u.last_name,
                'email': u.email,
                'role': role
            }
        return None

    if (current_user.is_admin()):
        user_query = User.query
        total_admins = len(user_query.filter_by(role=RoleEnum.ADMIN).all())
        total_users = len(user_query.all())
        total_students = len(Student.query.all())
        total_data_admins = len(User.query.filter(User.role==RoleEnum.DATA_ADMIN).all())
        user_list = [get_user_dict(u) for u in User.query.all()]
        name = current_user.first_name + ' ' + current_user.last_name

        return render_template('dashboard/admin.html', current_user=current_user, 
            user_name=name, total_admins=total_admins, total_users=total_users,
            total_students=total_students, total_data_admins=total_data_admins,
            user_list=user_list)
    else:
        return render_template('errors/403.html'), 403


@dash_bp.route('/change-role', methods = ['POST'])
@admin_required
@login_required
def change_role():
    body = request.get_json()
    if ('email' in body and 'new_role' in body):
        email = body['email']
        new_role = body['new_role']

        usr = User.query.get(email)
        
        if (usr):
            match new_role:
                case 'Admin':
                    usr.set_admin()
                case 'Data Admin':
                    usr.set_data_admin()
                case 'Viewer':
                    usr.set_viewer()
            return {'message': 'Success'}, 200
        else:
            return {'message': 'User not found'}, 400
    else:
        return {'message': 'Invalid request.'}, 400



@dash_bp.route('/upload', methods = ['POST'])
@admin_required
@login_required
def upload_data():
    if 'file' in request.files.keys():
        uploaded_file = request.files['file']
        return upload_csv_file(uploaded_file)
    else:
        return {'message': 'Missing file.'}, 400


@dash_bp.route('/all-data', methods = ['GET'])
@login_required
def all_data():
    if (len(request.data) != 0):
        body = request.get_json()
        limit = body['limit']
    else:
        limit = None

    data = ClassData.get_data()

    if (limit is not None and limit > len(data)):
        return {'message': 'Limit out of bounds.'}, 400
    else:
        data = ClassData.get_data(limit)
        return data, 200
        

@dash_bp.route('/average-dwf-rates', methods = ['POST'])
@login_required
def get_average_dwf_rates():
    body = request.get_json()

    if ('part' in body):
        part = body['part']
        if (part == 'highest'):
            return ClassData.get_avg_dwf_head(), 200
        elif (part == 'lowest'):
            return ClassData.get_avg_dwf_tail(), 200
        else:
            return {'message': 'Invalid part.'}, 400
    else:
        return {'message': 'Part missing.'}, 400


@dash_bp.route('/dwf-rates-csv/<part>', methods = ['GET'])
@login_required
def get_highest_and_lowest_dwf_rates(part: str):
    if (part != 'lowest' and part != 'highest' and part != 'both'):
        return {'message': 'Invalid part'}, 400
    else:
        if (part == 'lowest'):
            data_list = ClassData.get_avg_dwf_tail()
        elif (part == 'highest'):
            data_list = ClassData.get_avg_dwf_head()
        else:
            data_list = ClassData.get_awg_dwf_head_and_tail()
            part = 'highest_and_lowest'

        # Convert the data list to a pandas dataframe, then convert it to CSV.
        df = pd.DataFrame(data_list)
        csv_bytes = bytes(df.to_csv(lineterminator='\r\n', index=False),
             encoding='utf-8')

        # Return the CSV Bytes as a download to the user.
        res = make_response(csv_bytes)
        res.headers.set('Content-Type', 'text/csv')
        res.headers.set( 'Content-Disposition', 'attachment', 
            filename='%s_dwf_rates.csv' % part)
        return res


@dash_bp.route('/num-students-per-major-csv', methods = ['GET'])
@login_required
def get_num_students_per_major_as_csv():
    # Get the list of dict objects, then convert it to a cleaner readable format.
    data_list = Student.get_num_students_per_major()
    formatted_list = []
    for major_name in data_list:
        if (major_name != 'Total # of Students'):
            formatted_list.append({
                'major': major_name,
                'num_of_students': data_list[major_name]['num_of_students'],
                'percentage': data_list[major_name]['percentage']
            })

    # Create the dataframe, then convert it to CSV.
    df = pd.DataFrame(formatted_list)
    csv_bytes = bytes(df.to_csv(lineterminator='\r\n', index=False),
             encoding='utf-8')

    # Return the CSV Bytes as a download to the user.
    res = make_response(csv_bytes)
    res.headers.set('Content-Type', 'text/csv')
    res.headers.set( 'Content-Disposition', 'attachment', 
        filename='num_students_per_major.csv')
    return res


@dash_bp.route('/avg-gpa-and-dwf-per-semester', methods = ['GET'])
@login_required
def avg_gpa_per_semester():
    avg_gpas = Student.get_avg_gpa_per_semester()
    avg_dwfs = ClassData.get_dwf_rate_per_semester()

    return_dict = {}
    # Loop over the keys, creating a nested dict object.
    for key in avg_gpas.keys():
        return_dict[key] = {
            'avg_gpa': avg_gpas[key],
            'avg_dwf': avg_dwfs[key]
        }

    return return_dict, 200


@dash_bp.route('/avg-gpa-and-dwf-per-semester-csv', methods = ['GET'])
@login_required
def avg_gpa_per_semester_csv_download():
    avg_gpas = Student.get_avg_gpa_per_semester()
    avg_dwfs = ClassData.get_dwf_rate_per_semester()

    formatted_list = []
    # Loop over the keys, creating a nested dict object.
    for key in avg_gpas.keys():
        formatted_list.append({
            'semester': key,
            'avg_gpa': avg_gpas[key],
            'dwf_rate (percentage)': avg_dwfs[key]
        })

    # Create the dataframe, then convert it to CSV.
    df = pd.DataFrame(formatted_list)
    csv_bytes = bytes(df.to_csv(lineterminator='\r\n', index=False),
             encoding='utf-8')

    # Return the CSV Bytes as a download to the user.
    res = make_response(csv_bytes)
    res.headers.set('Content-Type', 'text/csv')
    res.headers.set( 'Content-Disposition', 'attachment', 
        filename='avg_gpa_and_dwf_per_semester.csv')
    return res


@dash_bp.route('/avg-gpa-per-cohort', methods = ['GET'])
@login_required
def avg_gpa_per_cohort():
    avg_gpas = ClassData.get_avg_gpa_per_cohort()
    return avg_gpas, 200


@dash_bp.route('/avg-gpa-per-cohort-csv', methods = ['GET'])
@login_required
def avg_gpa_per_cohort_csv_download():
     # Get the list of dict objects, then convert it to a cleaner readable format.
    data_list = ClassData.get_avg_gpa_per_cohort()
    formatted_list = []
    for cohort in data_list:
        formatted_list.append({
            'cohort': cohort,
            'avg_gpa': data_list[cohort]
        })

    # Create the dataframe, then convert it to CSV.
    df = pd.DataFrame(formatted_list)
    csv_bytes = bytes(df.to_csv(lineterminator='\r\n', index=False),
             encoding='utf-8')

    # Return the CSV Bytes as a download to the user.
    res = make_response(csv_bytes)
    res.headers.set('Content-Type', 'text/csv')
    res.headers.set( 'Content-Disposition', 'attachment', 
        filename='avg_gpa_per_cohort.csv')
    return res


@dash_bp.route('/course-semester-mapping', methods = ['GET'])
@login_required
def get_course_semester_mapping():
    course_semester_mapping = Course.get_course_semester_mapping()
    return course_semester_mapping, 200


@dash_bp.route('/class-by-class-comparisons', methods = ['POST'])
# @login_required
def class_by_class_comparisons():
    body = request.get_json()

    if ('column' not in body or 'selectedCourses' not in body):
        return {'message': 'Body missing information.'}, 400
    else:
        # Check to make sure at least 2 courses were selected.
        if (len(body['selectedCourses']) < 2):
            return {'message': 'At least 2 courses must be selected.'}, 400
        
        column = body['column']
        selected_courses = body['selectedCourses']

        return Utils.get_class_by_class_data(column, selected_courses), 200

@dash_bp.route('/covid-data-comparison', methods = ['POST'])
def covid_data_comparison():
    body = request.get_json()

    if ('covidData' not in body):
        return {'message': 'Body missing information.'}, 400
        
    # Check for valid keys in body.
    column = body['covidData']
    data = Utils.get_covid_data(column)
    return data, 200
