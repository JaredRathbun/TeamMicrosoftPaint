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


import jwt
from flask import current_app
import logging as logger
from flask_login import UserMixin
import enum
from app import db, app
import pyotp
from werkzeug.security import check_password_hash, generate_password_hash
import sqlalchemy
from sqlalchemy import (Column, Integer, Text, Float, CheckConstraint, Enum, 
    ForeignKey)
from itertools import groupby
from operator import attrgetter
from functools import cmp_to_key


class Utils:
    '''
    A utility class that contains static methods only.
    '''
    @staticmethod
    def group_table_by_column(table, column):
        '''
        Groups the specified table by the specified column.

        params:
            `table`: The table to query. `Ex. ClassData`
            `column`: The column to query. `Ex. ClassData.grade`

        return:
            A `list` of `list` objects, where each element in the list is each
            group, and each element in the lists is an `object` of the table.
        '''
        grouped_table = table.query.order_by(column).all()
        return [list(s) for i, s in groupby(grouped_table,
                                            attrgetter(str(column).split('.')[1]))]

    @staticmethod
    def get_class_by_class_data(column: str, selected_courses: dict) -> dict:
        '''
        Returns a `dict` with the data requested for each class specified.

        params:
            `column`: The column to compare each class by.
            `selected_courses`: A `dict` containing the courses and the semesters
            to compare each course.

        return:
            A `dict` containing the calculated/found data for each course.
        '''

        def get_class_data_column(column: str, course: str, semester: str,
                                  year: int) -> list[str] | float:
            '''
            Generates the correct calculated value for the provided column,
            course, semester, and year.

            params:
                `column`: A `str` holding the calculation to perform.
                Should be either 'grade' or 'avg_dwf_rate'.
                `course`: A `str` containing the course to get the data for.
                `semester`: A `str` containing the semester the course ran.
                `year`: An `int` containing the year the course ran.
            return:
                A `list` containing each of the grades for the course in the
                database or a float representing the average dwf rate for the
                course.
            '''
            course = Course.query.filter(Course.course_num ==
                    course and Course.semester == semester and Course.year ==
                                         year).first()

            if (column == 'grade'):
                class_data_entries = ClassData.query.filter(
                    ClassData.course_obj == course).all()
                return [course.grade for course in class_data_entries]
            else:
                class_data_entries = ClassData.query.filter(
                    ClassData.course_obj == course)
                dwf_grades = class_data_entries.filter(ClassData.grade == 'D' or
                    ClassData.grade == 'D+' or ClassData.grade == 'D-' or
                                                       ClassData.grade == 'W' or ClassData.grade == 'F').count()
                total_grades = class_data_entries.count()
                return round((dwf_grades / total_grades) * 100, 2) if total_grades > 0 else 0.0

        def get_student_data_column(column: str, course: str, semester: str,
                                    year: int) -> list | float:
            '''
            Generates the correct calculation for the given column, course,
            semester and year from the Student table.
            '''
            course = Course.query.filter(Course.course_num == course and
                                         Course.semester == semester and Course.year == year).first()
            class_data_objs = ClassData.query.filter(ClassData.course_obj ==
                                                     course).all()
            if (column == 'avg_high_school_gpa'):
                gpa_list = []
                for class_data_obj in class_data_objs:
                    hs_gpa = class_data_obj.student_obj.high_school_gpa

                    # Only get grades that are in the database, since
                    # high_school_gpa is nullable in the database.
                    if (hs_gpa is not None):
                        gpa_list.append(hs_gpa)

                gpa_list_len = len(gpa_list)
                return round(sum(gpa_list) / gpa_list_len, 2) if gpa_list_len > 0 else 0
            elif (column == 'avg_gpa'):
                gpa_list = []
                for class_data_obj in class_data_objs:
                    gpa = class_data_obj.student_obj.gpa_cumulative

                    # Only get grades that are in the database, since gpa is
                    # nullable in the database.
                    if (gpa is not None):
                        gpa_list.append(gpa)

                gpa_list_len = len(gpa_list)
                return round(sum(gpa_list) / gpa_list_len, 2) if gpa_list_len > 0 else 0
            else:
                column_list = []
                for class_data_obj in class_data_objs:
                    student = class_data_obj.student_obj

                    # Get the column of the Student table we are looking for.
                    column_val = getattr(student, column)

                    # If the column is a gpa, round it to 2 decimal places.
                    if (column == 'gpa_cumulative' or column ==
                            'high_school_gpa'):
                        column_val = round(column_val, 2)

                    # If the value is not None, add it to the column_list.
                    if (column_val is not None):
                        column_list.append(column_val)
                return column_list

        # Based on what column was selected, find which function to call.
        if (column == 'grade' or column == 'avg_dwf_rate'):
            function_to_call = get_class_data_column
        else:
            function_to_call = get_student_data_column

        return_data = {}
        for course_num in selected_courses:
            term = selected_courses[course_num]
            split_term = term.split(' ')
            semester = split_term[0]
            year = int(split_term[1])
            return_data[course_num] = function_to_call(
                column, course_num, semester, year)
        return return_data

    @staticmethod
    def get_avg_for_column(column, semester, year):
        '''
        '''
        all_class_data_objects = []

        for class_data_obj in ClassData.query.all():
            course_obj = class_data_obj.course_obj

            if (course_obj.semester == semester and course_obj.year == year):
                all_class_data_objects.append(class_data_obj)

        if (column != 'dwf_rate'):
            column_sum = 0
            column_entry_count = 0
            for cd in all_class_data_objects:
                attribute = getattr(cd.student_obj, column)
                if attribute != 0.0 and attribute != None:
                    column_sum += attribute
                    column_entry_count += 1

            return round((column_sum / column_entry_count), 2) if column_entry_count > 0 else 0
        else:
            dwf_count = 0
            total_num_grades_count = 0
            for cd in all_class_data_objects:
                # Access the grade for each ClassData entry
                grade = cd.grade

                # If there is a grade, its in ('D', 'D-', 'D+', 'W', 'F'), add
                # 1 to the count.
                if grade != None and grade in ('D', 'D-', 'D+', 'W', 'F'):
                    dwf_count += 1
                total_num_grades_count += 1

            return round(((dwf_count / total_num_grades_count) * 100), 2) if total_num_grades_count > 0 else 0

    @staticmethod
    def get_covid_data(column: str) -> dict:
        semesters = ['FA 2019', 'SP 2020', 'FA 2020', 'SP 2021', 'FA 2021']
        return_dict = {}

        column_to_query = None
        match column:
            case 'avg_gpa':
                # The column needed to get the student's gpa.
                column_to_query = 'gpa_cumulative'

            case 'avg_high_school_gpa':
                column_to_query = 'high_school_gpa'

            case 'avg_dwf_rate':
                column_to_query = 'dwf_rate'

            case 'avg_math_placement_score':
                column_to_query = 'math_placement_score'

            case 'avg_sat_total':
                column_to_query = 'sat_total'

            case 'avg_sat_math':
                column_to_query = 'sat_math'

            case 'avg_act_score':
                column_to_query = 'act_score'

            # You'll need to add these as you add more columns
            # avg_dwf is going to be a little harder since each grade lives in
            # the ClassData object and not the Student objects

        # Loop over every semester and get the average for that column.
        for semester in semesters:
            split_semester = semester.split(' ')
            semester_abbreviation = split_semester[0]
            year = int(split_semester[1])

            return_dict[semester] = Utils.get_avg_for_column(column_to_query,
                                                             semester_abbreviation, year)
        return return_dict

    @staticmethod
    def get_bar_chart_data(columnX: str, columnY: str) -> dict:
        
        data_dict = {}

        match columnX:
            case 'admit_term':
                columnX = Student.admit_term
            case 'admit_year':
                columnX = Student.admit_year
            case 'major_one':
                columnX = Student.major_1_desc
            case 'major_two':
                columnX = Student.major_2_desc
            case 'minor_one':
                columnX = Student.minor_1_desc
            case 'concentration':
                columnX = Student.concentration_desc
            case 'class_year':
                columnX = Student.class_year
            case 'city':
                columnX = Student.city
            case 'state':
                columnX = Student.state
            case 'race':
                columnX = Student.race_ethnicity
            case 'gender':
                columnX = Student.gender
            case 'hs_name':
                columnX = Student.high_school_name
            case 'hs_state':
                columnX = Student.high_school_state

        groups = Utils.group_table_by_column(Student, columnX)

        match columnY:
            case 'avg_gpa':
                columnY = 'gpa_cumulative'

            case 'avg_high_school_gpa':
                columnY = 'high_school_gpa'

            case 'avg_math_placement_score':
                columnY = 'math_placement_score'

            case 'avg_sat_total':
                columnY = 'sat_total'

            case 'avg_sat_math':
                columnY = 'sat_math'

        avg_col_val = Utils.get_avg_for_bar_data(groups, columnY)

            
        return data_dict

    @staticmethod
    def get_avg_for_bar_data(grouped, columnY):
        '''
        '''
        

    @staticmethod
    def get_all_data() -> list[dict]:
        '''
        Returns a list of dictionaries, where each dictionary is each entry in 
        the database.

        return:
            A `list` of `dict` objects containing information about each database
            entry.
        '''
        return_list = []
        for cd in ClassData.query.all():
            cd_dict = {}

            # Pull the info from the ClassData object.
            cd_dict['Unique_ID'] = cd.student_id
            cd_dict['Program_Level'] = cd.program_level
            cd_dict['Subprogram_Code'] = cd.subprogram_code
            cd_dict['Course_Grade'] = cd.grade

            # Pull the info from the Student object related to the ClassData.
            student_obj = cd.student_obj
            cd_dict['Admit_Year'] = student_obj.admit_year
            cd_dict['Admit_Term'] = student_obj.admit_term
            cd_dict['Admit_Type'] = student_obj.admit_type
            cd_dict['Major1_Code'] = student_obj.major_1
            cd_dict['Major1_Desc'] = student_obj.major_1_desc
            cd_dict['Major2_Code'] = student_obj.major_2
            cd_dict['Major2_Desc'] = student_obj.major_2_desc
            cd_dict['Minor1_Code'] = student_obj.minor_1
            cd_dict['Minor1_Desc'] = student_obj.minor_1_desc
            cd_dict['Concentration_Code'] = student_obj.concentration_code
            cd_dict['Concentration_Desc'] = student_obj.concentration_desc
            cd_dict['Class'] = student_obj.class_year.value
            cd_dict['City'] = student_obj.city
            cd_dict['State'] = student_obj.state
            cd_dict['Country'] = student_obj.country
            cd_dict['Postal_Code'] = student_obj.postal_code
            cd_dict['Sex'] = student_obj.gender
            cd_dict['Race-Ethnicity'] = student_obj.race_ethnicity
            cd_dict['Math_Placement_Score'] = student_obj.math_placement_score
            cd_dict['GPA_Cum'] = student_obj.gpa_cumulative
            cd_dict['SAT_Math'] = student_obj.sat_math
            cd_dict['SAT_Total'] = student_obj.sat_total
            cd_dict['ACT_Score'] = student_obj.act_score
            cd_dict['HS_GPA'] = student_obj.high_school_gpa
            cd_dict['HS_CEEB'] = student_obj.high_school_ceeb
            cd_dict['HS_Name'] = student_obj.high_school_name
            cd_dict['HS_City'] = student_obj.high_school_city
            cd_dict['HS_State'] = student_obj.high_school_state
            cd_dict['Cohort'] = student_obj.cohort

            # Pull the Course object that is related to the ClassData entry.
            course_obj = cd.course_obj
            cd_dict['Term'] = f'{course_obj.semester} {course_obj.year}'
            cd_dict['Course_Num'] = course_obj.course_num
            cd_dict['Numeric_Term_Code'] = course_obj.term_code

            return_list.append(cd_dict)
        return return_list

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
    FRESHMAN = 'Freshman'
    SOPHOMORE = 'Sophomore'
    JUNIOR = 'Junior'
    SENIOR = 'Senior'

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
    role = Column(Enum(RoleEnum), default=RoleEnum.VIEWER)
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

    def get_role(self) -> int:
        '''
        Returns the user's role.

        return:
            The correct `RoleEnum` object.
        '''
        return self.role

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
        return jwt.encode({'email': self.email},
                          current_app.config['SECRET_KEY'], algorithm='HS256')

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
                email = jwt.decode(token, current_app.config['SECRET_KEY'],
                                   algorithms=['HS256'])['email']
                return User.query.get(email)
            except Exception as e:
                return None
        else:
            return None

    def set_admin(self):
        '''
        Sets the user to an admin.
        '''
        self.role = RoleEnum.ADMIN
        self.gen_totp_key()
        db.session.commit()

    def set_data_admin(self):
        '''
        Sets the user to a data admin.
        '''
        self.role = RoleEnum.DATA_ADMIN
        self.gen_totp_key()
        db.session.commit()

    def set_viewer(self):
        '''
        Sets the user to a viewer.
        '''
        self.role = RoleEnum.VIEWER
        self.totp_key = None
        db.session.commit()

    def get_otp(self):
        '''
        Returns the TOTP OTP code for the user.

        return: 
            A `TOTP` object.
        '''
        if self.totp_key is None:
            raise InvalidPrivilegeException('User is not an admin!')
        return pyotp.TOTP(self.totp_key).now()

    def verify_otp(self, otp: str) -> bool:
        '''
        Verifies the user's OTP code.

        param:
            otp: The user's OTP code.
        return:
            A `bool` representing the result of the the comparison.
        '''
        
        if otp:
            return pyotp.TOTP(self.totp_key).verify(otp)
        else:
            return False

    def is_admin(self) -> bool:
        '''
        Returns whether or not the user is an admin.

        return:
            A `bool` representing if the user is an admin or not.
        '''
        return (self.role == RoleEnum.ADMIN)

    def is_data_admin(self) -> bool:
        '''
        Returns whether or not the user is a data admin.

        return:
            A `bool` representing if the user is a data admin or not.
        '''
        return (self.role == RoleEnum.DATA_ADMIN)


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
    def get_avg_gpa_per_semester() -> dict:
        '''
        Generates a dictionary containing the average gpa for each semester in
        the database.

        return:
            A `dict` containing the average gpa for each semester.
        '''
        semester_groups = Utils.group_table_by_column(
            ClassData, ClassData.course)

        return_dict = {}
        for group in semester_groups:
            semester = group[0].course_obj.semester
            year = group[0].course_obj.year

            avg_gpa = sum(
                [g.student_obj.gpa_cumulative for g in group]) / len(group)
            term = f'{semester} {year}'
            return_dict[term] = round(avg_gpa, 2)
        return return_dict

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

    @staticmethod
    def get_num_students_per_major() -> dict:
        '''
        Returns a `dict` containing each majors' number of students, the 
        percentage of the total students, and the correct bootstrap class to 
        style the colored bar with. The total number of students in the database
        is returned as a key in the `dict`.

        return:
            A `dict` containing each major in the database.
        '''
        def get_bootstrap_class(percentage: float) -> str:
            '''
            Returns the correct bootstrap class to style the colored bar with
            based on the percentage of students in a given major.

            param:
                `percentage`: A float containing the percentage of students in
                the major.
            return:
                A `str` containing the proper bootstrap class to style the
                colored bar with.
            '''
            match percentage:
                case percentage if percentage >= 0 and percentage <= 20:
                    return 'bg-danger'
                case percentage if percentage >= 21 and percentage <= 40:
                    return 'bg-warning'
                case percentage if percentage >= 41 and percentage <= 60:
                    return 'bg-primary'
                case percentage if percentage >= 61 and percentage <= 80:
                    return 'bg-info'
                case percentage if percentage >= 81 and percentage <= 100:
                    return 'bg-success'

        grouped_students = Student.query.order_by(Student.major_1_desc).all()
        total_num_students = len(grouped_students)
        grouped_students = [list(s) for i, s in groupby(grouped_students,
                                                        attrgetter('major_1_desc'))]
        return_dict = {'Total # of Students': total_num_students}
        for group in grouped_students:
            num_of_students = len(group)
            major = group[0].major_1_desc
            percentage = round((num_of_students / total_num_students) * 100, 2)
            return_dict[major] = {
                'num_of_students': num_of_students,
                'percentage': '{percent}%'.format(percent=percentage),
                'bootstrap_class': get_bootstrap_class(percentage)
            }

        return return_dict

    @staticmethod
    def get_avg_math_placement() -> str:
        '''
        Calculates the average math placement scores for all students in the database.

        return: 
            The average math placement scores of all students in the database represented by a `str`.
        '''
        def __sum_math_placement() -> int:
            '''
            Calculates the sum of all math placement scores in the database.

            return:
                An `int` holding the sum of all math placement scores in the database.
            '''
            sum = 0
            for student in Student.query.all():
                student_math_placement = student.math_placement_score
                if (student_math_placement is not None):
                    sum += student.math_placement_score
            return sum

        total_students = len(Student.query.all())
        math_score = __sum_math_placement()

        return '%.2f' % (math_score / total_students) if total_students > 0 else 0.0

    @staticmethod
    def get_avg_sat_total() -> str:
        '''
        Calculates the average math placement scores for all students in the database.

        return: 
            The average math placement scores of all students in the database represented by a `str`.
        '''
        def __sum_math_placement() -> int:
            '''
            Calculates the sum of all math placement scores in the database.

            return:
                An `int` holding the sum of all math placement scores in the database.
            '''
            sum = 0
            for student in Student.query.all():
                student_math_placement = student.math_placement_score
                if (student_math_placement is not None):
                    sum += student.math_placement_score
            return sum

        total_students = len(Student.query.all())
        math_score = __sum_math_placement()

        return '%.2f' % (math_score / total_students) if total_students > 0 else 0.0

    @staticmethod
    def get_avg_sat_math() -> str:
        '''
        Calculates the average math sat scores for all students in the database.

        return: 
            The average math sat scores of all students in the database represented by a `str`.
        '''
        def __sum_math() -> int:
            '''
            Calculates the sum of all math sat scores in the database.

            return:
                An `int` holding the sum of all math sat scores in the database.
            '''
            sum = 0
            for student in Student.query.all():
                student_math_sat = student.sat_math
                if (student_math_sat is not None):
                    sum += student.sat_math
            return sum

        total_students = len(Student.query.all())
        math_score = __sum_math()

        return '%.2f' % (math_score / total_students) if total_students > 0 else 0.0

    @staticmethod
    def get_avg_act() -> str:
        '''
        Calculates the average math sat scores for all students in the database.

        return: 
            The average math sat scores of all students in the database represented by a `str`.
        '''
        def __sum_math() -> int:
            '''
            Calculates the sum of all math sat scores in the database.

            return:
                An `int` holding the sum of all math sat scores in the database.
            '''
            sum = 0
            for student in Student.query.all():
                student_math_sat = student.sat_math
                if (student_math_sat is not None):
                    sum += student.sat_math
            return sum

        total_students = len(Student.query.all())
        math_score = __sum_math()

        return '%.2f' % (math_score / total_students) if total_students > 0 else 0.0


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
        num_with_dwf = len(class_data.filter(ClassData.grade =='F' or 
            ClassData.grade =='W' or ClassData.grade=='D' or 
            ClassData.grade =='D-' or ClassData.grade=='D+').all())

        return '%.2f' % ((num_with_dwf / num_grades) * 100) if num_grades > 0 else 0.0

    @classmethod
    def get_avg_dwf_per_course(cls) -> list[dict]:
        '''
        Returns a `list` of `dict` objects with the average DWF for each course.

        return:
            A `list` of `dict` objects with each course's number, the DWF rate, 
            and semester it ran.
        '''
        dwf_list = []
        grouped_courses = ClassData.query.order_by(ClassData.course).all()
        grouped_courses = [list(c) for i, c in groupby(
            grouped_courses, attrgetter('course_obj'))]
        # Loop over every group, getting the class and DWF rate for each class.
        for course_group in grouped_courses:
            course_obj = course_group[0].course_obj
            semester = course_obj.semester
            course_num = course_obj.course_num
            year = course_obj.year

            # Get the grades, then make a call to get the avg DWF.
            course_grades = [c.grade for c in course_group]
            length = len(course_grades)
            dwf_len = len(list(filter(lambda c: c == 'W' or c == 'D+' or c == 'D'
                                      or c == 'D-' or c == 'F', course_grades)))
            avg_dwf = ((dwf_len / length) * 100) if length > 0 else 0.0

            # Add a dict to the list of each class.
            dwf_list.append({
                'course_num': course_num,
                'semester': semester,
                'year': year,
                'avg_dwf':  avg_dwf
            })

        # Sort the list, then return it.
        sorted_list = sorted(
            dwf_list, key=lambda e: e['avg_dwf'], reverse=True)

        # Format the DWF rates in each class to be 2 decimal places.
        for clazz in sorted_list:
            clazz['avg_dwf'] = '%.2f' % clazz['avg_dwf']

        return sorted_list

    @staticmethod
    def get_avg_dwf_head() -> list[dict]:
        '''
        Returns the top 5 courses with the highest DWF rates.

        return:
            A `list` of `dict` objects with the top 5 courses.
        '''

        # Get the list of sorted classes.
        dwf_list = ClassData.get_avg_dwf_per_course()

        if (len(dwf_list) < 5):
            return dwf_list
        else:
            return dwf_list[0:5]

    @staticmethod
    def get_avg_dwf_tail() -> list[dict]:
        '''
        Returns the top 5 courses with the lowest DWF rates.

        return:
            A `list` of `dict` objects with the top 5 courses.
        '''

        # Get the list of sorted classes.
        dwf_list = ClassData.get_avg_dwf_per_course()

        if (len(dwf_list) < 5):
            return dwf_list
        else:
            dwf_list = dwf_list[-5:]
            dwf_list.reverse()
            return dwf_list

    @staticmethod
    def get_awg_dwf_head_and_tail():
        '''
        Returns the top 5 courses with the highest DWF rates and the top 5 
        courses with the lowest DWF rates.

        return:
            A `list` of `dict` objects containing information about each course.
        '''

        # Get the list of sorted classes.
        dwf_list = ClassData.get_avg_dwf_per_course()

        return_list = dwf_list[0:5]
        return_list.append({})
        lowest = dwf_list[-5:]
        lowest.reverse()
        return_list += lowest

        return return_list

    @staticmethod
    def get_dwf_rate_per_semester():
        '''
        Returns a dictionary with the dwf rate per semester.

        return:
            A `dict` of semesters mapped to each DWF rate.
        '''
        grouped_class_data = Utils.group_table_by_column(ClassData,
                                                         ClassData.course)
        return_dict = {}
        for course_group in grouped_class_data:
            # Get the grades, then make a call to get the avg DWF.
            course_grades = [c.grade for c in course_group]
            length = len(course_grades)
            dwf_len = len(list(filter(lambda c: c == 'W' or c == 'D+' or c == 'D'
                                      or c == 'D-' or c == 'F', course_grades)))
            term = f'{course_group[0].course_obj.semester} {course_group[0].course_obj.year}'
            return_dict[term] = round(
                (dwf_len / length) * 100, 2) if length > 0 else 0

        return return_dict

    @staticmethod
    def get_data(limit: int=None) -> list[dict]:
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

    @staticmethod
    def get_avg_grade() -> str:
        '''
        Returns the average letter grade for all class grades in the database.

        return:
            A `str` representing the average course grade.
        '''
        all_grades = []

        grade_to_num = {
            'A+': 13, 'A': 12, 'A-': 11, 'B+': 10, 'B': 9, 'B-': 8, 'C+': 7,
            'C': 6, 'C-': 5, 'D+': 4, 'D': 3, 'D-': 2, 'F': 1
        }

        num_to_grade = {
            13: 'A+', 12: 'A', 11: 'A-', 10: 'B+', 9: 'B', 8: 'B-', 7: 'C+',
            6: 'C', 5: 'C-', 4: 'D+', 3: 'D', 2: 'D-', 1: 'F'
        }

        for class_data in ClassData.query.all():
            if (class_data.grade != 'W' and class_data.grade != 'IP' and
                    class_data.grade != 'P'):
                all_grades.append(grade_to_num[class_data.grade])

        if (len(all_grades) != 0):
            return num_to_grade[round(sum(all_grades) / len(all_grades))]
        else:
            return 'N/A'

    def get_avg_gpa_per_cohort():
        '''
        Returns a `dict` containing the average student GPA for each class cohort.

        return:
            A `dict` containing the average student gpa per cohort.
        '''
        grouped_cohorts = Utils.group_table_by_column(
            Student, Student.class_year)
        return_dict = {}
        for group in grouped_cohorts:
            gpas = [s.gpa_cumulative for s in group]
            summed_gpa = sum(gpas)
            return_dict[group[0].class_year.value] = round(
                summed_gpa / len(gpas), 2) if len(gpas) > 0 else 0
        return return_dict


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

    @staticmethod
    def get_course_semester_mapping() -> dict[str, list]:
        '''
        Returns a mapping of all the semesters each class has data in the 
        database for.

        return:
            A `dict` object mapping each class to the semesters it ran.
        '''
        def semester_sort(semester1: str, semester2: str) -> int:
            '''
            Sorting function for semesters in the semester_list for each course.

            params:
                semester1: The first semester to compare.
                semester2: The second semester to compare.
            return:
                A `int` representing the order of the sorting.
            '''
            semester1_split = semester1.split(' ')
            semester2_split = semester2.split(' ')

            semester1_year = int(semester1_split[1])
            semester2_year = int(semester2_split[1])

            if (semester1_year < semester2_year):
                return -1
            elif (semester1_year > semester2_year):
                return 1
            else:
                return 0

        grouped_course_nums = Utils.group_table_by_column(
            Course, Course.course_num)
        mapping_dict = {}

        # Walk over every group of each course, getting each semester and adding
        # to a list.
        for group in grouped_course_nums:
            course_num = group[0].course_num
            semester_list = []
            for course in group:
                semester_list.append(f'{course.semester} {course.year}')
            semester_list.sort(key=cmp_to_key(semester_sort))
            mapping_dict[course_num] = semester_list
        return mapping_dict

    @staticmethod
    def get_list_of_years() -> list:
        '''
        Returns a list of all the years input into the database.

        return:
            A `list` of years.
        '''
        years = set()
        course_list = Course.query.all()
        for course in course_list:
            years.add(course.year)

        return sorted(list(years))

    @staticmethod
    def get_highest_lowest_years() -> dict:
        '''
        Returns the lowest and highest year in the data.

        return:
            An 'dict' that shows the lowest and highest year.
        '''
        year_list = Course.get_list_of_years()

        years = {
            'lowest': year_list[0],
            'highest': year_list[-1]
        }

        return years

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
