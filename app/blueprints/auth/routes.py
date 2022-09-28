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


from flask import render_template, request, redirect, url_for
from . import auth_bp, oauth_client
from app.models import ExistingPasswordException, InvalidProviderException, ProviderEnum, User
import base64
from flask_login import current_user, login_user, logout_user, login_required
from . import app
import requests
import json
from flask_mail import Message
from app import mail

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
                    login_user(usr)
                    return redirect('/dashboard')
            else:
                return {'message': 'Failed Login'}, 401
        
        return {'message': 'Failed Login'}, 401


@auth_bp.route('/oauth/login', methods = ['GET'])
@auth_bp.route('/oauth/register', methods = ['GET'])
def oauth_login():
    google_provider = requests.get(app.config['GOOGLE_DISCOVERY_URL']).json()
    auth_endpoint = google_provider['authorization_endpoint']

    return redirect(oauth_client.prepare_request_uri(
        auth_endpoint, redirect_uri=request.base_url + 
            '/callback', scope=['openid', 'email', 'profile']
    ))


@auth_bp.route('/oauth/login/callback', methods = ['GET'])
@auth_bp.route('/oauth/register/callback', methods = ['GET'])
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
        if usr.is_admin:
            # May want to change to redirect the user to an OTP page.
            return {'message': 'Successful Admin Login'}, 202 
        else: 
            login_user(usr)
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
@auth_bp.route('/otp/<user>', methods = ['POST'])
def otp(user):
    usr = User.query.get(user)
    # Change to check OTP and login if success.
    login_user(usr)
    return {'message': 'success'}, 200


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


@auth_bp.route('/logout', methods = ['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/login')