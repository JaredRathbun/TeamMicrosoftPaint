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


from app import login_manager
from flask import Blueprint
from app.models import User
from app import app
from oauthlib.oauth2 import WebApplicationClient

# Register the login manager.
@login_manager.user_loader
def load_user(email: str):
    '''
    Loads the user from the database based on their email address.
    '''
    return User.query.get(email)

# Register the blueprint.
auth_bp = Blueprint('auth', __name__)

oauth_client = WebApplicationClient(app.config['GOOGLE_CLIENT_ID'])