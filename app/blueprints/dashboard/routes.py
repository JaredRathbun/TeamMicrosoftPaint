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




from . import dash_bp
from flask import render_template, request
from flask_login import login_required, current_user
from app import admin_required
from app.blueprints.dashboard.data_upload import upload_excel_file
from app.models import User, ClassData, Course, Student

@dash_bp.route('/dashboard', methods = ['GET'])
@login_required
def get_dash():
    name = current_user.first_name + ' ' + current_user.last_name
    dwf_avg = ClassData.get_avg_dwf()
    avg_gpa = Student.get_avg_gpa()
    high_school_avg_gpa = Student.get_avg_high_school_gpa()
    total_students = len(Student.query.all())

    return render_template('dashboard/dashboard.html', current_user=current_user,
        user_name=name, dwf_avg=dwf_avg, avg_gpa=avg_gpa, 
        high_school_avg_gpa=high_school_avg_gpa, total_students=total_students)


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
    high_school_avg_gpa = Student.get_avg_high_school_gpa()
    total_students = len(Student.query.all())
    return render_template('dashboard/visualizations.html', 
        current_user=current_user, user_name=name, dwf_avg=dwf_avg, 
        avg_gpa=avg_gpa, high_school_avg_gpa=high_school_avg_gpa, 
        total_students=total_students)


@dash_bp.route('/admin', methods = ['GET'])
@login_required
@admin_required
def get_admin():
    def get_user_dict(u: User) -> str:
        '''
        Returns a `str` representation of whether or not the user is admin.
        '''
        if u:
            return {
                'name': u.first_name + ' ' + u.last_name,
                'email': u.email,
                'permissions': lambda x: 'Admin' if u.is_admin else 'User'
            }
        return None

    if (current_user.is_admin):
        user_query = User.query
        total_admins = len(user_query.filter_by(is_admin=True).all())
        total_users = len(user_query.all())
        total_students = len(Student.query.all())
        rows_in_dataset = len(ClassData.query.all())
        user_admin_list = [get_user_dict(u) for u in User.query.all()]
        name = current_user.first_name + ' ' + current_user.last_name

        return render_template('dashboard/admin.html', current_user=current_user, 
            user_name=name, total_admins=total_admins, total_users=total_users,
            total_students=total_students, rows_in_dataset=rows_in_dataset,
            user_admin_list=user_admin_list)
    else:
        return render_template('errors/403.html'), 403


@dash_bp.route('/upload', methods = ['POST'])
@admin_required
@login_required
def upload_data():
    if 'file' in request.files.keys():
        uploaded_file = request.files['file']
        return upload_excel_file(uploaded_file)
    else:
        return {'message': 'Missing file.'}, 400


@dash_bp.route('/all-data', methods = ['GET'])
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
        