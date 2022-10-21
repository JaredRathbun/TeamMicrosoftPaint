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
    LOCAL, GOOGLE = range(2)


class RoleEnum(enum.Enum):
    VIEWER, DATA_ADMIN, ADMIN = range(3)


class ClassEnum(enum.Enum):
    FRESHMAN, SOPHOMORE, JUNIOR, SENIOR = range(4)

    @staticmethod
    def parse_class(class_str: str):
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
                return InvalidClassException('Class not recognized.')

    
    @staticmethod 
    def class_to_str(class_year) -> str:
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
    pass


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

    def is_active():
        return True

    def is_authenticated():
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
        return: A `bool` representing whether or not the operation was successful.
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
        else:
            return False


class Student(db.Model):
    __tablename__ = 'students'
    id = Column(Text(), primary_key=True)
    admit_year = Column(Integer(), nullable=False)
    admit_term = Column(Text(), nullable=False)
    admit_type = Column(Text(), nullable=False)
    major = Column(Text(), nullable=False)
    major_desc = Column(Text(), nullable=False)
    concentration_code = Column(Text())
    concentration_desc = Column(Text())
    class_year = Column(Enum(ClassEnum), nullable = False)
    city = Column(Text())
    state = Column(Text())
    country = Column(Text())
    postal_code = Column(Text(), nullable=False)
    math_placement_score = Column(Integer())
    race_ethnicity = Column(Text(), nullable=False)
    gender = Column(Text(), nullable=False)
    gpa_cumulative = Column(Float(), 
        CheckConstraint('gpa_cumulative >= 0.0 AND gpa_cumulative <= 4.0'))
    math_placement_score = Column(Integer())
    high_school_gpa = Column(Float(), 
        CheckConstraint('high_school_gpa >= 0.0 AND high_school_gpa <= 4.0'))
    sat_math = Column(Integer(), 
        CheckConstraint(f'sat_math >= {app.config["SAT_SCORE_MIN"]} AND sat_math <= {app.config["SAT_SCORE_MAX"]}'))
    sat_total = Column(Integer(), 
        CheckConstraint(f'sat_total >= {app.config["SAT_SCORE_MIN"]} AND sat_total <= {app.config["SAT_SCORE_MAX"]}'))
    high_school_name = Column(Text())
    high_school_city = Column(Text())
    high_school_state = Column(Text())
    high_school_ceeb = Column(Integer())


    @staticmethod
    def get_avg_gpa() -> str:
        '''
        Calculates the average college GPA for all students in the database.

        return: The average GPA of all students in the database represented by 
            a str.
        '''
        def __sum_gpa():
            '''
            Calculates the sum of all college GPAs in the database.
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
        
        for i in range(limit):   
            current_class = class_data[i]
            current_student = current_class.student_obj
            current_course = current_class.course_obj

            def format_leave_date(date):
                if (date is not None):
                    return date.strftime('%m-%d-%Y')
                else:
                    return None

            def format_home_location(city: str, state: str, country: str) -> str:
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

            def format_high_school_info(student):
                gpa = student.high_school_gpa
                name = student.high_school_name
                city = student.high_school_city
                state = student.high_school_state
                ceeb = student.high_school_ceeb

                if (city is not None and state is not None):
                    location = f'{"" if (city is None) else city}, {"" if (state is None) else state}'
                elif (city is None and state is not None):
                    location = state
                elif (city is not None and state is None):
                    location = city
                else:
                    location = 'N/A'
                    
                return {
                    'gpa': '' if (gpa is None) else gpa,
                    'name': '' if (name is None) else name,
                    'location': location,
                    'ceeb': '' if (ceeb is None) else ceeb
                }

            current_dict = {
                'student_id': current_class.student_id,
                'course_code': current_course.course_num,
                'program_level': current_class.program_level,
                'subprogram_code': current_class.subprogram_code,
                'semester': current_course.semester,
                'year': current_course.year,
                'grade': current_class.grade,
                'demographics': {
                    'race_ethnicity': current_student.race_ethnicity,
                    'gender': current_student.gender,
                    'home_location': format_home_location(current_student.city,
                        current_student.state, current_student.country),
                    'home_zip_code': '' if (current_student.postal_code is None) 
                        else current_student.postal_code 
                },
                'academic_info': {
                    'major': current_student.major_desc,
                    'concentration': current_student.concentration_desc,
                    'class_year': ClassEnum.class_to_str(current_student.class_year),
                    'college_gpa': current_student.gpa_cumulative,
                    'math_placement_score': current_student.math_placement_score,
                    'sat_math': current_student.sat_math,
                    'sat_total': current_student.sat_total,
                    'admit_term_year': f'{current_student.admit_term} {current_student.admit_year}', 
                    'admit_type': current_student.admit_type
                },
                'high_school_info': format_high_school_info(current_student)
            }
            return_list.append(current_dict)
        return return_list


class Course(db.Model):
    __tablename__ = 'courses'
    id = Column(Integer(), primary_key=True)
    term_code = Column(Text(), nullable=False)
    course_num = Column(Text(), CheckConstraint('length(course_num) >= 7 AND length(course_num) <= 9'), 
        nullable=False)
    semester = Column(Text(), CheckConstraint('semester IN ("FA", "SP", "WI", "SU")'), 
        nullable=False)
    year = Column(Integer(), nullable=False)

    
    def __repr__(self):
        return f'{self.id} - {self.course_num} - {self.title}'