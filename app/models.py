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


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, jsonify
import logging as logger
from flask_login import UserMixin
import enum
from app import db, app
import pyotp
from werkzeug.security import check_password_hash, generate_password_hash
import sqlalchemy
from sqlalchemy import (Column, Integer, Text, Float, Boolean, CheckConstraint,
    Enum, DateTime, ForeignKey)
import secrets


class ProviderEnum(enum.Enum):
    LOCAL = 1
    GOOGLE = 2


class InvalidProviderException(Exception):
    pass


class ExistingPasswordException(Exception):
    pass


class InvalidPrivilegeException(Exception):
    pass


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    email = Column(Text(), primary_key=True)
    last_name = Column(Text(), nullable=False)
    first_name = Column(Text(), nullable=False)
    hash = Column(Text())
    totp_key = Column(Text())
    is_admin = Column(Boolean(), nullable=False, default=False)
    provider = Column(Enum(ProviderEnum))

    def __init__(self, email, first_name, last_name, password=None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

        if password:
            self.hash = generate_password_hash(password)
            self.provider = ProviderEnum.LOCAL
        else:
            self.provider = ProviderEnum.GOOGLE

    def get_id(self):
        return self.email


    def is_active(self):
        return True


    def is_authenticated(self):
        return True


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
        raise InvalidProviderException


    def gen_totp_key(self):
        '''
        Generates the TOTP Key for this user and saves it.
        '''
        self.totp_key = pyotp.random_base32()


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
            logger.error('Unable to insert new user.', e)
            db.session.rollback()
            return False

    def set_password(self, new_password: str):
        '''
        Changes the user's password, provided it is not the same as the current
        password.

        param:
            new_password: The user's new password.
        return: A `bool` representing whether or not the operation was successful.
        raises:
            `TypeError` if the new password is an empty `str`.
            `ExistingPasswordException` if the new password is the same as the
            current password.
        '''
        if new_password is None or new_password.strip() == '':
            raise TypeError('New password was empty.')
            
        if self.check_password(new_password):
            raise ExistingPasswordException()
            
        # Generate the new hash and commit it to the database.
        self.hash = generate_password_hash(new_password)
        db.session.commit()
        return True


    def get_reset_token(self, duration=1800) -> str:
        '''
        Gets a reset token for the given user.
        
        param: duration=1800 The amount of time the token is valid for.
        return: The token represented as a string.
        '''
        return Serializer(current_app.config['SECRET_KEY'], duration).dumps(
            {'email': self.email}).decode('utf-8')

    
    @staticmethod
    def verify_reset_token(token: str):
        if token:
            try:
                email = Serializer(current_app.config['SECRET_KEY']).loads(
                    token)['email']
                return User.query.get(email)
            except Exception as e:
                return None
        return None


    def set_admin(self):
        '''
        Sets the user to an admin.
        '''
        self.is_admin = True
        self.gen_totp_key()
        db.session.commit()


    def get_otp(self):
        '''
        Returns the TOTP OTP code for the user.

        return: An `TOTP` object.
        '''
        if self.totp_key is None:
            raise InvalidPrivilegeException('User is not an admin!')
        return pyotp.TOTP(self.totp_key, interval=120)

    
    def verify_otp(self, otp: str) -> bool:
        '''
        Verifies the user's OTP code.

        param:
            otp: The user's OTP code.
        return:
            A `bool` representing the result of the the comparison.
        '''
        if otp: 
            correct_otp = self.get_otp().now()
            return correct_otp == otp
        return False


class Student(db.Model):
    __tablename__ = 'students'
    id = Column(Integer(), primary_key=True)
    last_name = Column(Text(), nullable=False)
    first_name = Column(Text(), nullable=False)
    major_1 = Column(Text(), nullable=False)
    major_2 = Column(Text())
    major_3 = Column(Text())
    concentration_1 = Column(Text())
    concentration_2 = Column(Text())
    concentration_3 = Column(Text())
    minor_1 = Column(Text())
    minor_2 = Column(Text())
    minor_3 = Column(Text())
    math_placement_score = Column(Integer())
    high_school_gpa = Column(Float(), 
        CheckConstraint('high_school_gpa >= 0.0 AND high_school_gpa <= 4.0'))
    college_gpa = Column(Float(), 
        CheckConstraint('high_school_gpa >= 0.0 AND high_school_gpa <= 4.0'))
    sat_score = Column(Integer(), 
        CheckConstraint(f'sat_score >= {app.config["SAT_SCORE_MIN"]} AND sat_score <= {app.config["SAT_SCORE_MAX"]}'))
    act_score = Column(Integer(), 
        CheckConstraint(f'act_score >= {app.config["ACT_SCORE_MIN"]} AND act_score <= {app.config["ACT_SCORE_MAX"]}'))
    state_code = Column(Text(), nullable=False)
    country_code = Column(Text(), nullable=False)
    leave_date = Column(DateTime())
    first_gen_student = Column(Boolean())


    @staticmethod
    def gen_random_id():
        # Get all the ids in the table, sorted.
        all_ids = list(map(lambda s: s.id, Student.query.all()))
        
        # Generate a random id.
        gen_id = secrets.randbelow(1999999) + 1000000

        # Keep generating until a unique id is found.
        while gen_id in all_ids:
            gen_id = secrets.randbelow(1999999) + 1000000

        return gen_id


class ClassData(db.Model):
    __tablename__ = 'class_data'
    dummy_pk = Column(Integer(), primary_key=True)
    student_id = Column(Integer(), nullable=False)
    program_code = Column(Text(), CheckConstraint('program_code IN ("UNDG", "GRAD")'), 
        nullable=False)
    subprogram_desc = Column(Text(), nullable=False)
    course_title = Column(Text(), nullable=False)
    course_num = Column(Text(), 
        CheckConstraint('length(course_num) >= 7 AND length(course_num) <= 8'), 
        nullable=False)
    final_grade = Column(Text(), nullable=False)
    course_semester = Column(Text(), nullable=False)
    course_year = Column(Integer(), CheckConstraint('course_year <= date()'),
         nullable=False)


class MCASScore(db.Model):
    __tablename__ = 'mcas_scores'
    student_id = Column(Integer(), ForeignKey('students.id'), primary_key=True, 
        nullable=False)
    english_raw = Column(Integer(), CheckConstraint(f'english_raw >= {app.config["MCAS_RAW_MIN"]} AND english_raw <= {app.config["MCAS_RAW_MAX"]}'))
    english_scaled = Column(Integer(), CheckConstraint(f'english_scaled >= {app.config["MCAS_SCALED_MIN"]} AND english_scaled <= {app.config["MCAS_SCALED_MAX"]}'))
    english_achievement_level = Column(Text(), CheckConstraint('english_achievement_level IN ("F", "NI", "P", "A")'))
    math_raw = Column(Integer(), CheckConstraint(f'math_raw >= {app.config["MCAS_RAW_MIN"]} AND math_raw <= {app.config["MCAS_RAW_MAX"]}'))
    math_scaled = Column(Integer(), CheckConstraint(f'math_scaled >= {app.config["MCAS_SCALED_MIN"]} AND math_scaled <= {app.config["MCAS_SCALED_MAX"]}'))
    math_achievement_level = Column(Text(), CheckConstraint('math_achievement_level IN ("F", "NI", "P", "A")'))
    stem_raw = Column(Integer(), CheckConstraint(f'stem_raw >= {app.config["MCAS_RAW_MIN"]} AND stem_raw <= {app.config["MCAS_RAW_MAX"]}'))
    stem_scaled = Column(Integer(), CheckConstraint(f'stem_scaled >= {app.config["MCAS_SCALED_MIN"]} AND stem_scaled <= {app.config["MCAS_SCALED_MAX"]}'))
    stem_achievement_level = Column(Text(), CheckConstraint('stem_achievement_level IN ("F", "NI", "P", "A")'))