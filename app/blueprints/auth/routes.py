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


from flask import render_template, request, redirect, url_for
from . import auth_bp, oauth_client
from app.models import (ExistingPasswordException, InvalidProviderException, 
    ProviderEnum, User, InvalidPrivilegeException, RoleEnum)
import base64
from flask_login import current_user, login_user, logout_user, login_required
from . import app
import requests
import json
from flask_mail import Message
from app import mail
import re


MERRIMACK_EMAIL_REGEX = r'x*@merrimack.edu'

def send_reset_email(email: str) -> bool:
    usr = User.query.get(email)
    
    if usr is None or usr.provider == ProviderEnum.GOOGLE:
        return False
    else:
        token = usr.get_reset_token()
        msg = Message('STEM Data Dashboard | Password Reset Request',
                sender=app.config['MAIL_USERNAME'],
                recipients=[usr.email])
        msg.body = f'''
            To reset your password, please visit the following link:
            {url_for('auth.reset', token=token, _external=True)}
            If you did not make this request please reset your password immediately.
            '''
        mail.send(msg)
        return True

def send_otp_email(usr: User) -> bool:
    if usr is None:
        return False
    else:
        otp = usr.get_otp().now()
        msg = Message('STEM Data Dashboard | 2-Factor Authentication',
            sender=app.config['MAIL_USERNAME'],
            recipients=[usr.email])
        msg.body = f'''Your OTP (One Time Passcode) is {otp}. If you did not submit a request for this code, please consider changing your password.
                '''
        mail.send(msg)
        return True


@auth_bp.route('/', methods = ['GET'])
def base_route():
    if current_user.is_authenticated:
        return redirect('/dashboard')
    else:
        return redirect('/login')


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
            return redirect('/dashboard')
        else:
            return render_template('auth/login.html')
    else:
        body = request.get_json()

        if 'email' not in body or 'password' not in body:
            return {'Bad Request'}, 400

        if re.search(MERRIMACK_EMAIL_REGEX, body['email']):
            return {'message': 'Cannot login with merrimack.edu email.'}, 406        

        usr = User.query.get(body['email'])

        if usr:
            # Decode the password.
            password = base64.b64decode(body['password']).decode('utf-8')
            
            try:
                login_success = usr.check_password(password)
            except InvalidProviderException:
                return {'message': 'Failed Login'}, 401

            if login_success:
                needs_2fa = (usr.role == RoleEnum.ADMIN or usr.rol == RoleEnum.DATA_ADMIN)
                login_user(usr)

                if needs_2fa:
                    return redirect(f'/otp/{usr.email}')
                else: 
                    return redirect('/dashboard')
            else:
                return {'message': 'Failed Login'}, 401
        
        return {'message': 'Failed Login'}, 401


@auth_bp.route('/oauth/login', methods = ['GET'])
def oauth_login():
    google_provider = requests.get(app.config['GOOGLE_DISCOVERY_URL']).json()
    auth_endpoint = google_provider['authorization_endpoint']

    return redirect(oauth_client.prepare_request_uri(
        auth_endpoint, redirect_uri=request.base_url + 
            '/callback', scope=['openid', 'email', 'profile']
    ))


@auth_bp.route('/oauth/login/callback', methods = ['GET'])
def oauth_login_callback():
    code = request.args.get('code')
    google_provider = requests.get(app.config['GOOGLE_DISCOVERY_URL']).json()
    token_endpoint = google_provider['token_endpoint']

    token_url, headers, body = oauth_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_res = requests.post(token_url, headers=headers, data=body, 
        auth=(app.config['GOOGLE_CLIENT_ID'], 
            app.config['GOOGLE_CLIENT_SECRET'])
    )

    oauth_client.parse_request_body_response(json.dumps(token_res.json()))

    user_info_endpoint = google_provider['userinfo_endpoint']
    uri, headers, body = oauth_client.add_token(user_info_endpoint)
    res = requests.get(uri, headers=headers, data=body).json()

    usr = User.query.get(res['email'])

    if usr:
        login_user(usr)
        if usr.is_admin() or usr.is_data_admin():
            return redirect(f'/otp/{usr.email}')
        else:
            return redirect('/dashboard')
    else:
        # If the user doesn't exist, register them.
        if len(res['name'].split(" ")) > 2:
            first_name, last_name = res['name'].split(" ")[0], res['name'].split(" ")[1]
        else:
            first_name, last_name = res['name'].split(" ")
        new_usr = User(res['email'], first_name, last_name)
        if User.insert_user(new_usr):
            login_user(new_usr)
            return redirect('/dashboard')
        else:
            return {'message': 'Failed to enroll user.'}, 500
        

@login_required
@auth_bp.route('/otp/<email>', methods = ['GET', 'POST'])
def otp(email):
    usr = User.query.get(email)
    if not usr:
        return {'message': 'User not found'}, 400

    if request.method == 'GET':
        try:
            send_otp_email(usr)
        except InvalidPrivilegeException:
            return {'message': 'User is not an admin.'}, 403


        return render_template('auth/otp.html', 
            name=usr.first_name + ' ' + usr.last_name)
    else:
        # Change to check OTP and login if success.
        body = request.get_json()
        if 'otp' in body:
            if usr.verify_otp(body['otp']): 
                return redirect('/dashboard') 
            else:
                return {'message': 'Invalid OTP Code'}, 401
        else:
            return {'message': 'Invalid request.'}, 400


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
            return {'message': 'Invalid Request'}, 400
        else:
            email = body['email']
            first_name = body['first_name']
            last_name = body['last_name']
            password = base64.b64decode(body['password']).decode('utf-8')
            
            if User.query.get(email):
                return {'message': 'User exists'}, 409
            else:
                if re.search(MERRIMACK_EMAIL_REGEX, email):
                    return {'message': 'User has merrimack.edu email.'}, 406
                else:
                    new_user = User(email, first_name, last_name, password)
                    if User.insert_user(new_user):
                        return redirect('/login')
                    else:
                        return {'message': 'Failed to enroll user.'}, 500
                
                
@auth_bp.route('/sendreset', methods = ['GET', 'POST'])
def send_email():
    if request.method == 'GET':
        return render_template('auth/sendreset.html')
    else:
        # Need to figure out how to send reset email here.
        email = request.get_json()['email']

        if email.strip() != '':
            if send_reset_email(email):
                return {'message': 'Success'}, 200
            else:
                return {'message': 'User not found.'}, 400
        return {'message': 'Failed to send email.'}, 400

    
@auth_bp.route('/reset', methods = ['GET', 'POST'])
def reset():
    if request.method == 'GET':
        return render_template('auth/reset.html')
    else:
        body = request.get_json()

        if ('token' not in body or 'password' not in body):
            return {'message': 'Invalid request'}, 400
        else:
            usr = User.verify_reset_token(body['token'])
            
            if usr:
                # Check make sure they are local.
                if usr.provider == ProviderEnum.LOCAL:
                    try:
                        usr.set_password(base64.b64decode(body['password'])
                            .decode('utf-8'))
                        return redirect('/login')
                    except TypeError:
                        return {'message': 'Password cannot be blank.'}, 400
                    except ExistingPasswordException:
                        return {'message': 'Cannot reuse old password.'}, 409
                else:
                    return {'message': 'Account with local provider not found.'}, 400
            else:
                return {'message': 'User not found.'}, 400


@auth_bp.route('/logout', methods = ['POST'])
def logout():
    logout_user()
    return redirect('/login')