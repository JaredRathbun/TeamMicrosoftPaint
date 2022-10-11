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

@dash_bp.route('/dashboard', methods = ['GET'])
@login_required
def get_dash():
    name = current_user.first_name + ' ' + current_user.last_name
    return render_template('dashboard.html', user_name=name)


@dash_bp.route('/data', methods = ['GET'])
@login_required
def get_data():
    name = current_user.first_name + ' ' + current_user.last_name
    return render_template('data.html', user_name=name)


@dash_bp.route('/upload', methods = ['POST'])
# @admin_required
# @login_required
def upload_data():
    if 'file' in request.files.keys():
        uploaded_file = request.files['file']
        return upload_excel_file(uploaded_file)
    else:
        return {'message': 'Missing file.'}, 400