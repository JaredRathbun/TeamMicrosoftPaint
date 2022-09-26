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


from flask import render_template, request, make_response, redirect
from . import auth_bp, oauth_client
from app.models import InvalidProviderException, User
import base64
from flask_login import current_user


@auth_bp.route('/login', methods = ['GET', 'POST'])
def login():
    '''
    Handles serving the /login template, or handles a login POST request.

    GET:
        renders the auth/login.html template.
    POST:
        verifies the user's email and password against the database. The body of
        the response should follow this format:

        {
            'email': 'XXX@XXX.XXX',
            'password': 'dGVzdDEyMw==' <-- Base64 Encoded
        }
    '''
    if request.method == 'GET':
        if current_user.is_authenticated:
            redirect('/dashboard')
        else:
            return render_template('auth/login.html')
    else:
        body = request.get_json()

        if 'email' not in body or 'password' not in body:
            return {'Bad Request'}, 400

        usr = User.query.get(body['email'])

        if usr:
            # Decode the password.
            password = base64.b64decode(body['password']).decode('utf-8')
            
            try:
                login_success = usr.check_password(password)
            except InvalidProviderException:
                return {'message': 'Failed Login'}, 401

            if login_success:
                is_admin = usr.is_admin

                if is_admin:
                    return {'message': 'Successful Admin Login'}, 202 
                else: 
                    return redirect('/dashboard')
            else:
                return {'message': 'Failed Login'}, 401
        
        return {'message': 'Failed Login'}, 401

@auth_bp.route('oauth/login', methods = [])

@auth_bp.route('/register', methods = ['GET', 'POST'])
def register():
    '''
    Handles serving the register.html template and registering users.
    '''
    if request.method == 'GET':
        return render_template('auth/register.html')
    else:
        body = request.get_json()
        if ('email' not in body or 'first_name' not in body or 
            'last_name' not in body or 'password' not in body):
            return {'Invalid Request'}, 400
        else:
            email = body['email']
            first_name = body['first_name']
            last_name = body['last_name']
            password = base64.b64decode(body['password']).decode('utf-8')
            
            if User.query.get(email):
                return {'message': 'User exists'}, 409
            else:
                new_user = User(email, first_name, last_name, password)
                if User.insert_user(new_user):
                    return {'message': 'Success'}, 200
                else:
                    return {'message': 'Failed to enroll user.'}, 500
                
                
@auth_bp.route('/reset', methods = ['GET', 'POST'])
def reset():
    if request.method == 'GET':
        return render_template('auth/reset.html')
    else:
        body = request.get_json()

        if 'email' not in body:
            return {'message': 'Email not provided'}, 400
        else:
            # Need to email a reset link to the user here.
            pass