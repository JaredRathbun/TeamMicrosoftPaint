from flask import Blueprint, render_template, url_for, request
from app import login_manager
from app.models import User

# Register the login manager.
@login_manager.user_loader
def load_user(email: str):
    '''
    Loads the user from the database based on their email address.
    '''
    return User.query.get(email)

# Register the blueprint.
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods = ['GET', 'POST'])
@auth_bp.route('/auth/login', methods = ['GET'])
def get_login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    else:
        body = request.data
        print(body)