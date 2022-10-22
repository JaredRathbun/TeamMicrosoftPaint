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


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
import logging as logger
from flask_login import UserMixin
import enum
from app import db, app
import pyotp
from werkzeug.security import check_password_hash, generate_password_hash
import sqlalchemy
from sqlalchemy import (Column, Integer, Text, Float, Boolean, CheckConstraint,
    Enum, ForeignKey)


class ProviderEnum(enum.Enum):
    '''
    An Enum to represent the method of how a user is authenticating to the system.
    '''
    LOCAL, GOOGLE = range(2)


class RoleEnum(enum.Enum):
    '''
    An Enum to hold the valid roles assigned to users.
    '''
    VIEWER, DATA_ADMIN, ADMIN = range(3)


class ClassEnum(enum.Enum):
    '''
    An Enum to represent a student's class (year of education).
    '''
    FRESHMAN, SOPHOMORE, JUNIOR, SENIOR = range(4)
 
    @staticmethod
    def parse_class(class_str: str) -> int:
        '''
        Parses a `str` object into a `ClassEnum` object. 

        param: 
            `class_str` The `str` representation of the class.
        return: 
            A `ClassEnum` object representing the student's class.
        raises: 
            `InvalidClassException` If the class could not be parsed.
        '''
        match class_str:
            case 'FR':
                return ClassEnum.FRESHMAN
            case 'SO':
                return ClassEnum.SOPHOMORE
            case 'JR':
                return ClassEnum.JUNIOR
            case 'SR':
                return ClassEnum.SENIOR
            case _:
                raise InvalidClassException('Class not recognized.')

    
    @staticmethod 
    def class_to_str(class_year) -> str:
        '''
        Converts a `ClassEnum` object into a `str` format.

        param: 
            `class_year` The `ClassEnum` object of to parse.
        return: 
            A `str` representing the student's class.
        '''
        match class_year:
            case ClassEnum.FRESHMAN:
                return 'Freshman'
            case ClassEnum.SOPHOMORE:
                return 'Sophomore'
            case ClassEnum.JUNIOR:
                return 'Junior'
            case ClassEnum.SENIOR:
                return 'Senior'
            case _:
                return ''


class InvalidClassException(Exception):
    '''
    An exception to represent an invalid class.
    '''
    pass


class InvalidProviderException(Exception):
    '''
    An exception to represent an invalid provider.
    '''
    pass


class ExistingPasswordException(Exception):
    '''
    An exception to represent an existing password conflict.
    '''
    pass


class InvalidPrivilegeException(Exception):
    '''
    An exception to represent an invalid privilege.
    '''
    pass


class User(UserMixin, db.Model):
    '''
    A class to represent a user.
    '''
    __tablename__ = 'users'
    email = Column(Text(), primary_key=True)
    last_name = Column(Text(), nullable=False)
    first_name = Column(Text(), nullable=False)
    hash = Column(Text())
    totp_key = Column(Text())
    is_admin = Column(Boolean(), nullable=False, default=False)
    provider = Column(Enum(ProviderEnum))

    def __init__(self, email, first_name, last_name, password=None):
        '''
        Creates a new `User` object.
        '''
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

        # If the password exists, a local account is being created. Otherwise,
        # a Google account is being used to log in.
        if password:
            self.hash = generate_password_hash(password)
            self.provider = ProviderEnum.LOCAL
        else:
            self.provider = ProviderEnum.GOOGLE

    def get_id(self) -> str:
        '''
        Getter for the user's email address.

        return: 
            A `str` representing the user's email address.
        '''
        return self.email

    def is_active() -> bool:
        '''
        Returns if the user is active or not.

        return: 
            `True`
        '''
        return True

    def is_authenticated():
        '''
        Returns whether or not the user is authenticated.

        return: `True`
        '''
        return True

    def check_password(self, password: str):
        '''
        Verifies the provided password against the hashed password.

        param:
            password: The password the user entered.
        return:
            A `bool` representing whether or not the password was correct.
        raises:
            An `InvalidProviderException` if the user's provider is not `ProviderEnum.LOCAL`.
        '''
        if self.provider is ProviderEnum.LOCAL:
            return check_password_hash(self.hash, password)
        else:
            raise InvalidProviderException()

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
        return: 
            A `bool` representing whether or not the operation was successful.
        raises:
            `TypeError` if the new password is an empty `str`.
            `ExistingPasswordException` if the new password is the same as the
            current password.
        '''
        if new_password is None or new_password.strip() == '':
            raise TypeError('New password was empty.')
        else:
            if self.check_password(new_password):
                raise ExistingPasswordException()
            else:
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
        '''
        Verifies whether or not the user's password reset token is valid.
        
        param:
            `token`: A `str` representing the user's token.

        return: 
            A `User` corresponding to the user.
        '''
        if token:
            try:
                email = Serializer(current_app.config['SECRET_KEY']).loads(
                    token)['email']
                return User.query.get(email)
            except Exception as e:
                return None
        else:
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

        return: 
            A `TOTP` object.
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
        else:
            return False


class Student(db.Model):
    ''''
    A class to hold a Student.
    '''
    __tablename__ = 'students'
    id = Column(Text(), primary_key=True)
    admit_year = Column(Integer(), nullable=False)
    admit_term = Column(Text(), nullable=False)
    admit_type = Column(Text(), nullable=False)
    major_1 = Column(Text(), nullable=False)
    major_1_desc = Column(Text(), nullable=False)
    major_2 = Column(Text())
    major_2_desc = Column(Text())
    minor_1 = Column(Text())
    minor_1_desc = Column(Text())
    concentration_code = Column(Text())
    concentration_desc = Column(Text())
    class_year = Column(Enum(ClassEnum), nullable=False)
    city = Column(Text(), nullable=False)
    state = Column(Text())
    country = Column(Text(), nullable=False)
    postal_code = Column(Text(), nullable=False)
    math_placement_score = Column(Integer())
    race_ethnicity = Column(Text(), nullable=False)
    gender = Column(Text(), nullable=False)
    gpa_cumulative = Column(Float(), 
        CheckConstraint('gpa_cumulative >= 0.0 AND gpa_cumulative <= 4.0'))
    high_school_gpa = Column(Float(), 
        CheckConstraint('high_school_gpa >= 0.0 AND high_school_gpa <= 4.0'))
    sat_math = Column(Integer(), 
        CheckConstraint(f'sat_math >= {app.config["SAT_SCORE_MIN"]} AND sat_math <= {app.config["SAT_SCORE_MAX"]}'))
    sat_total = Column(Integer(), 
        CheckConstraint(f'sat_total >= {app.config["SAT_SCORE_MIN"]} AND sat_total <= {app.config["SAT_SCORE_MAX"]}'))
    act_score = Column(Integer(), 
        CheckConstraint(f'act_score >= {app.config["ACT_SCORE_MIN"]} AND act_score <= {app.config["ACT_SCORE_MAX"]}'))
    high_school_name = Column(Text())
    high_school_city = Column(Text())
    high_school_state = Column(Text())
    high_school_ceeb = Column(Integer())
    cohort = Column(Text())
    mcas_score_obj = db.relationship('MCASScore', uselist=False)

    @staticmethod
    def get_avg_gpa() -> str:
        '''
        Calculates the average college GPA for all students in the database.

        return: 
            The average GPA of all students in the database represented by a `str`.
        '''
        def __sum_gpa() -> int:
            '''
            Calculates the sum of all college GPAs in the database.

            return:
                An `int` holding the sum of all GPAs in the database.
            '''
            sum = 0
            for student in Student.query.all():
                student_gpa = student.gpa_cumulative
                if (student_gpa is not None):
                    sum += student.gpa_cumulative
            return sum

        total_students = len(Student.query.all())
        gpa_sum = __sum_gpa()

        return '%.2f' % (gpa_sum / total_students) if total_students > 0 else 0.0


    @staticmethod
    def get_avg_high_school_gpa() -> str:
        '''
        Calculates the average high school GPA for all students in the database.

        return: The average high school GPA of all students in the database 
                represented by a str.
        '''
        def __sum_gpa():
            '''
            Calculates the sum of all high school GPAs in the database.
            '''
            sum = 0
            for student in Student.query.all():
                student_hs_gpa = student.high_school_gpa
                if (student_hs_gpa is not None):
                    sum += student.high_school_gpa
            return sum

        total_students = len(Student.query.all())
        gpa_sum = __sum_gpa()

        return '%.2f' % (gpa_sum / total_students) if total_students > 0 else 0.0 


class ClassData(db.Model):
    '''
    A Class to hold Class Data.
    '''
    __tablename__ = 'class_data'
    dummy_pk = Column(Integer(), primary_key=True)
    student_id = Column(Integer(), ForeignKey('students.id'), nullable=False)
    program_level = Column(Text(), nullable=False)
    subprogram_code = Column(Integer(), nullable=False)
    grade = Column(Text(), CheckConstraint("grade in ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'W', 'IP', 'P')"), 
        nullable=False)
    course = Column(Integer(), ForeignKey('courses.id'), nullable=False)
    course_obj = db.relationship('Course', uselist=False)
    student_obj = db.relationship('Student', uselist=False)


    @staticmethod
    def get_avg_dwf() -> float:
        '''
        Calculates the average DWF rate of all the data in the database.

        return: 
            A `float` reprenting the average DWF rate of all students in the 
            database.
        '''
        class_data = ClassData.query
        num_grades = len(class_data.all())
        num_with_dwf = len(class_data.filter(ClassData.grade=='F' or 
            ClassData.grade=='W' or ClassData.grade=='D' or 
            ClassData.grade=='D-' or ClassData.grade=='D+').all())
        
        return (num_with_dwf / num_grades) * 100 if num_grades > 0 else 0.0 


    @staticmethod
    def get_data(limit: int=None) -> list[dict] :
        '''
        Returns a list of dictionaries, which contain the information for each
        `ClassData` entry, along with the student, MCAS score, and class related
        to the entry.

        param: 
            limit: The max number of entries to generate. If the limit is not 
                supplied, then all entries are returned.

        return:
            A `list` of `dict` objects that contain the information about each
            class entry and the data related to it.
        '''
        class_data = ClassData.query.all()
        return_list = []

        # If the limit is not specified, set it to the max amount.
        if (limit is None):
            limit = len(class_data)
        
        # Loop over every ClassData object in the database, within the limit.
        for i in range(limit):   
            current_class = class_data[i]
            current_student = current_class.student_obj
            current_course = current_class.course_obj
            current_mcas_scores = current_student.mcas_score_obj

            def format_home_location(city: str, state: str, country: str) -> str:
                '''
                Formats the student's home location.

                param:
                    `city`: The student's city in a `str`.
                    `state`: The student's state in a `str`.
                    `country`: The student's country in a `str`.
                return:
                    A formatted `str` representing the student's home location. 
                    Returns a blank `str` if all 3 parameters were of `NoneType`.
                '''
                if (city is not None and state is not None and country is not None):
                    return f'{city}, {state}, {country}'
                elif (city is not None and state is not None):
                    return f'{city}, {state}'
                elif (city is not None and country is not None):
                    return f'{city}, {country}'
                elif (state is not None and country is not None):
                    return f'{state}, {country}'
                else:
                    return ''

            def format_info(info: object) -> str:
                '''
                Converts the info `object` into either N/A or the correct 
                `str` representation of the `object`.

                param:
                    info: A `object` representing the info.
                return:
                    A `str` holding either the info or 'N/A'.
                '''
                if (info is None):
                    return 'N/A'
                else:
                    return info

            def format_mcas_scores() -> dict:
                '''
                Formats the student's MCAS Scores into a `dict` object.

                param: 
                    `score_obj`: The `MCASScore` object.
                return:
                    A `dict` holding the student's MCAS scores.
                '''
                if (current_mcas_scores is not None):
                    return {
                        'english_raw': format_info(current_mcas_scores.english_raw),
                        'english_scaled': format_info(current_mcas_scores.english_scaled),
                        'english_achievement_level': format_info(current_mcas_scores.english_achievement_level),
                        'math_raw': format_info(current_mcas_scores.math_raw),
                        'math_scaled': format_info(current_mcas_scores.math_scaled),
                        'math_achievement_level': format_info(current_mcas_scores.math_achievement_level),
                        'stem_raw': format_info(current_mcas_scores.stem_raw),
                        'stem_scaled': format_info(current_mcas_scores.stem_scaled),
                        'stem_achievement_level': format_info(current_mcas_scores.stem_achievement_level)
                    }

            def format_demographics() -> dict:
                '''
                Creates a `dict` object for the student's demographic information.

                return:
                    A `dict` object containing the student's demographics.
                '''
                city = current_student.high_school_city
                state = current_student.high_school_state

                if (city is not None and state is not None):
                    location = f'{"" if (city is None) else city}, {"" if (state is None) else state}'
                elif (city is None and state is not None):
                    location = state
                elif (city is not None and state is None):
                    location = city
                else:
                    location = 'N/A'
                
                return {
                    'race_ethnicity': current_student.race_ethnicity,
                    'gender': current_student.gender,
                    'home_location': format_home_location(current_student.city,
                        current_student.state, current_student.country),
                    'home_zip_code': '' if (current_student.postal_code is None) 
                        else current_student.postal_code,
                    'high_school_name': format_info(current_student.high_school_name),
                    'high_school_location': location,
                    'high_school_ceeb': format_info(current_student.high_school_ceeb)
                }

            def format_academic_info() -> dict:
                '''
                Formats the student's academic info in a `dict` object.

                return:
                    A `dict` object containing the student's academic info.
                '''
                return {
                    'cohort': format_info(current_student.cohort),
                    'major_1': current_student.major_1_desc,
                    'major_2': format_info(current_student.major_2_desc),
                    'minor_1': format_info(current_student.minor_1_desc),
                    'concentration': format_info(current_student.concentration_desc),
                    'class_year': ClassEnum.class_to_str(current_student.class_year),
                    'admit_term_year': f'{current_student.admit_term} {current_student.admit_year}', 
                    'admit_type': current_student.admit_type
                }

            def format_academic_scores() -> dict:
                '''
                Formats the student's academic scores and returns them in a 
                `dict` object.

                return:
                    A `dict` containing the student's academic scores.
                '''
                return {
                    'college_gpa': format_info(current_student.gpa_cumulative),
                    'math_placement_score': format_info(current_student.math_placement_score),
                    'sat_math': format_info(current_student.sat_math),
                    'sat_total': format_info(current_student.sat_total),
                    'act_score': format_info(current_student.act_score),
                    'high_school_gpa': format_info(current_student.high_school_gpa)
                }

            # Create the dict for this ClassData object, and append it to the 
            # return list.
            current_dict = {
                'student_id': current_class.student_id,
                'course_code': current_course.course_num,
                'program_level': current_class.program_level,
                'subprogram_code': current_class.subprogram_code,
                'semester': current_course.semester,
                'year': current_course.year,
                'grade': current_class.grade,
                'demographics': format_demographics(),
                'academic_info': format_academic_info(),
                'academic_scores': format_academic_scores()
                # 'mcas_scores': format_mcas_scores()
            }
            return_list.append(current_dict)
        return return_list


class Course(db.Model):
    '''
    A class to represent a Course.
    '''
    __tablename__ = 'courses'
    id = Column(Integer(), primary_key=True)
    term_code = Column(Text(), nullable=False)
    course_num = Column(Text(), CheckConstraint('length(course_num) >= 7 AND length(course_num) <= 9'), 
        nullable=False)
    semester = Column(Text(), CheckConstraint('semester IN ("FA", "SP", "WI", "SU")'), 
        nullable=False)
    year = Column(Integer(), nullable=False)


class MCASScore(db.Model):
    '''
    A class to represent MCAS scores.
    '''
    __tablename__ = 'mcas_scores'
    student_id = Column(Text(), ForeignKey('students.id'), primary_key=True, 
        nullable=False)
    english_raw = Column(Integer())
    english_scaled = Column(Integer())
    english_achievement_level = Column(Text())
    math_raw = Column(Integer())
    math_scaled = Column(Integer())
    math_achievement_level = Column(Text())
    stem_raw = Column(Integer())
    stem_scaled = Column(Integer())
    stem_achievement_level = Column(Text())