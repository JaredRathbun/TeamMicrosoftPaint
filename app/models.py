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
    overall_college_gpa = Column(Float(), 
        CheckConstraint('overall_college_gpa >= 0.0 AND overall_college_gpa <= 4.0'))
    major_college_gpa = Column(Float(), 
        CheckConstraint('major_college_gpa >= 0.0 AND major_college_gpa <= 4.0'))
    sat_score = Column(Integer(), 
        CheckConstraint(f'sat_score >= {app.config["SAT_SCORE_MIN"]} AND sat_score <= {app.config["SAT_SCORE_MAX"]}'))
    act_score = Column(Integer(), 
        CheckConstraint(f'act_score >= {app.config["ACT_SCORE_MIN"]} AND act_score <= {app.config["ACT_SCORE_MAX"]}'))
    ethnicity = Column(Text(), nullable=False)
    state_code = Column(Text(), nullable=False)
    country_code = Column(Text(), nullable=False)
    leave_date = Column(DateTime())
    leave_reason = Column(Text())
    first_gen_student = Column(Boolean())
    mcas_score_obj = db.relationship('MCASScore', uselist=False)


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


    @staticmethod
    def get_avg_overall_gpa() -> str:
        '''
        Calculates the average overall GPA for all students in the database.

        return: The average overall GPA of all students in the database 
                represented by a str.
        '''
        def __sum_gpa():
            '''
            Calculates the sum of all overall college GPAs in the database.
            '''
            sum = 0
            for student in Student.query.all():
                sum += student.overall_college_gpa
            return sum

        total_students = len(Student.query.all())
        gpa_sum = __sum_gpa()

        return '%.2f' % (gpa_sum / total_students) if total_students > 0 else 0.0


    @staticmethod
    def get_avg_major_gpa() -> str:
        '''
        Calculates the average major GPA for all students in the database.

        return: The average major GPA of all students in the database 
                represented by a str.
        '''
        def __sum_gpa():
            '''
            Calculates the sum of all major college GPAs in the database.
            '''
            sum = 0
            for student in Student.query.all():
                sum += student.major_college_gpa
            return sum

        total_students = len(Student.query.all())
        gpa_sum = __sum_gpa()

        return '%.2f' % (gpa_sum / total_students) if total_students > 0 else 0.0 


class ClassData(db.Model):
    __tablename__ = 'class_data'
    dummy_pk = Column(Integer(), primary_key=True)
    student_id = Column(Integer(), ForeignKey('students.id'), nullable=False)
    program_code = Column(Text(), CheckConstraint('program_code IN ("UNDG", "GRAD")'), 
        nullable=False)
    subprogram_desc = Column(Text(), nullable=False)
    final_grade = Column(Text(), nullable=False)
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
        num_with_dwf = len(class_data.filter(ClassData.final_grade=='F' or 
            ClassData.final_grade=='W' or ClassData.final_grade=='D' or 
            ClassData.final_grade=='D-' or ClassData.final_grade=='D+').all())
        
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
            current_mcas_scores = current_student.mcas_score_obj
            current_course = current_class.course_obj

            def format_leave_date(date):
                if (date is not None):
                    return date.strftime('%m-%d-%Y')
                else:
                    return None

            def get_mcas_score_dict(score_obj):
                if (score_obj is not None):
                    return {
                        'english_raw': score_obj.english_raw,
                        'english_scaled': score_obj.english_scaled,
                        'english_achievement_level': score_obj.english_achievement_level,
                        'math_raw': score_obj.math_raw,
                        'math_scaled': score_obj.math_scaled,
                        'math_achievement_level': score_obj.math_achievement_level,
                        'stem_raw': score_obj.stem_raw,
                        'stem_scaled': score_obj.stem_scaled,
                        'stem_achievement_level': score_obj.stem_achievement_level
                    }
                else:
                    return {
                        'english_raw': None,
                        'english_scaled': None,
                        'english_achievement_level': None,
                        'math_raw': None,
                        'math_scaled': None,
                        'math_achievement_level': None,
                        'stem_raw': None,
                        'stem_scaled': None,
                        'stem_achievement_level': None
                    }

            current_dict = {
                'student_id': current_class.student_id,
                'course_code': current_course.course_num,
                'course_title': current_course.title,
                'semester': current_course.semester,
                'year': current_course.year,
                'final_grade': current_class.final_grade,
                'subprogram_desc': current_class.subprogram_desc,
                'demographics': {
                    'first_name': current_student.first_name,
                    'last_name': current_student.last_name,
                    'major_1': current_student.major_1,
                    'major_2': current_student.major_2,
                    'major_3': current_student.major_3,
                    'concentration_1': current_student.concentration_1,
                    'concentration_2': current_student.concentration_2,
                    'concentration_3': current_student.concentration_3,
                    'minor_1': current_student.minor_1,
                    'minor_2': current_student.minor_2,
                    'minor_3': current_student.minor_3,
                    'ethnicity': current_student.ethnicity,
                    'home_location': f'{current_student.state_code}, {current_student.country_code}',
                    'first_gen_student': current_student.first_gen_student
                },
                'academic_info': {
                    'overall_college_gpa': current_student.overall_college_gpa,
                    'major_college_gpa': current_student.major_college_gpa,
                    'high_school_gpa': current_student.high_school_gpa,
                    'math_placement_score': current_student.math_placement_score,
                    'sat_score': current_student.sat_score,
                    'act_score': current_student.act_score,
                    'leave_date': format_leave_date(current_student.leave_date),
                    'leave_reason': current_student.leave_reason 
                },
                'mcas_info': get_mcas_score_dict(current_mcas_scores)
            }
            return_list.append(current_dict)
        return return_list


class MCASScore(db.Model):
    __tablename__ = 'mcas_scores'
    student_id = Column(Integer(), ForeignKey('students.id'), primary_key=True, 
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


class Course(db.Model):
    __tablename__ = 'courses'
    id = Column(Integer(), primary_key=True)
    course_num = Column(Text(), CheckConstraint('length(course_num) >= 7 AND length(course_num) <= 9'), 
        nullable=False)
    title = Column(Text(), nullable=False)
    semester = Column(Text(), CheckConstraint('semester IN ("FA", "SP", "WI")'), 
        nullable=False)
    year = Column(Integer(), nullable=False)

    
    def __repr__(self):
        return f'{self.id} - {self.course_num} - {self.title} '