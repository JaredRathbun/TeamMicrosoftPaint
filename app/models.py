import logging as logger
from flask_login import UserMixin
import enum
from app import db
import pyotp
import sqlalchemy
from werkzeug.security import check_password_hash, generate_password_hash

class ProviderEnum(enum.Enum):
    LOCAL = 1
    PROVIDER = 2

class InvalidProviderException(Exception):
    pass

class User(UserMixin, db.Model):
    __tablename__ = 'USERS'
    email = db.Column(db.String(255), primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    hash = db.Column(db.String(60))
    totp_key = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean(), nullable=False, default=False)
    provider = db.Column(db.Enum(ProviderEnum))

    def __init__(self, email, first_name, last_name, password=None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

        if password:
            self.hash = generate_password_hash(password)
            self.provider = ProviderEnum.LOCAL
        else:
            self.provider = ProviderEnum.GOOGLE


    def check_password(self, password: str):
        '''
        Verifies the provided password against the hashed password.

        param: 
            password: The password the user entered.
        return:
            A `bool` representing whether or not the password was correct.
        '''
        if self.provider is ProviderEnum.LOCAL:
            return check_password_hash(self.hash, password)
        else:
            raise InvalidProviderException
            

    def gen_totp_key(self):
        '''
        Generates the TOTP Key for this user and saves it.
        '''
        return pyotp.random_base32()

    @staticmethod
    def insert_user(usr):
        '''
        Attempts to enroll a new `User` into the database.

        param: 
            usr: The new `User` object to add to the database.
        return:
            A `bool` representing if the insertion was sucessful or not.
        '''
        try:
            db.session.add(usr)
            db.session.commit()
            return True
        except sqlalchemy.exc.IntegrityError as e:
            logger.error('IntegrityError while adding new user.', e)
            db.session.rollback()
            return False