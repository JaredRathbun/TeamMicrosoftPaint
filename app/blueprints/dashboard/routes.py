from . import dash_bp
from flask import render_template
from flask_login import login_required, current_user


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