from flask import render_template, request, make_response, redirect
from . import auth_bp
from app.models import InvalidProviderException, User
import base64


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
                