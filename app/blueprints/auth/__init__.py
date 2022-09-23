from app import login_manager
from flask import Blueprint
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
