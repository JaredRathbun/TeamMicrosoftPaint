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


from app import init_app
import logging
from os import environ


if __name__ == '__main__':
    '''
    Launches the app.
    '''
    # Call the function in the app module to create the Flask object.
    app = init_app()
    app.app_context().push()

    # Get the environment variable set by the run script.
    env = environ['env']

    # Run the app based on the environment. 
    if (env == 'dev'):
        # Run on all addresses.
        app.run('0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'], ssl_context=('instance/cert.pem', 'instance/key.pem'))
    elif (env == 'test'):
        app.run('0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'], ssl_context=('instance/cert.pem', 'instance/key.pem'))
    elif (env == 'prod'):
        # Run on just localhost.
        app.run('127.0.0.1', port=app.config['PORT'], debug=app.config['DEBUG'], ssl_context=('instance/cert.pem', 'instance/key.pem'))
    else:
        print('Incorrect environment, please use either "dev" or "prod."')
        exit(1)