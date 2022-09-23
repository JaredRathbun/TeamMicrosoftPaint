import pytest
from app import init_app
from os.path import abspath as abspath
from os import environ as environ

@pytest.fixture(scope='module')
def test_client():
    app = init_app('test.cfg')
    app.testing = True
    app.config['Testing'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] =  abspath('test/test.db')
    app.config['SECRET_KEY'] = 'dev'
    app.config['EMAIL_PASS_PATH'] = 'Capstone1@'

    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

# https://gitlab.com/patkennedy79/flask_user_management_example/-/blob/main/tests/conftest.py#L12
# https://testdriven.io/blog/flask-pytest/