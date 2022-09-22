from flask import Blueprint, render_template

# Register the blueprint.
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods = ['GET'])
def get_login():
    return render_template('login.html')