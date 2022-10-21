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


from datetime import datetime
from werkzeug.datastructures import FileStorage
import pandas as pd
from pandas import DataFrame
from app.models import Student, ClassData, Course
from app import db, app
import re

error_list = []
has_errors = False

# A list of IDs for students that had an error.
failed_students = []

class InvalidDataException(Exception):
    '''
    An exception to hold an invalid data entry.
    '''
    def __init__(self, message, line_num):
        super().__init__(message)
        self.message = message
        self.line_num = line_num
    

    def __repr__(self) -> str:
        return f'{super().__repr__()} at line num: {self.line_num}'

def upload_excel_file(data: FileStorage):
    '''
    Parses the specified excel file and inserts it into the database.

    param: 
        data: The `FileStorage` object containing the excel file.

    return:
        A `Response` object representing the response to be returned to the API
        call.
    '''
    if not data:
        return {'message': 'Unable to read file'}, 400
    else:
        # Split the sheets.
        excel_file = pd.ExcelFile(data)
        students = pd.read_excel(excel_file, 'students')
        class_data = pd.read_excel(excel_file, 'class_data')
        mcas_scores = pd.read_excel(excel_file, 'mcas_scores')

        id_mapping = __insert_students(students)
        __insert_class_data(class_data, id_mapping)
        

        # If there were no errors, commit the database and return the success msg.
        if len(error_list) == 0:
            db.session.commit()
            return {'message': 'Success.'}, 200
        else:
            # Process the errors into JSON, then clear the list of errors.
            error_json = __process_errors(error_list)
            error_list.clear()
            return {'message': 'Errors while parsing data.', 
                'errors': error_json}, 400


def __insert_class_data(class_data: DataFrame, id_mapping: dict[int]):
    '''
    Inserts all Class Data into the database. Also reports invalid/missing data
    and inserts the error into the `error_list`.

    param:
        class_data: The `DataFrame` object containing the class_data worksheet.
        id_mapping: The `dict` of student IDs mapped to random IDs.
    '''
    # Replace all nans with None.
    class_data = class_data.astype(object).where(class_data.notna(), None)

    for idx in class_data.index:
        current_row = idx + 2
        found_error = False
        random_id = None
        valid_course_data = True

        try:
            random_id = id_mapping[class_data['Student ID'][idx]]
        except KeyError:
            error_list.append(InvalidDataException('Matching student not ' +
                'found for Class Data Entry', current_row))
            found_error = True

        program_code = class_data['Program Code'][idx]
        subprogram_desc = class_data['Subprogram Description'][idx]
        course_title = class_data['Course Title'][idx]
        course_num = class_data['Course Number'][idx]
        grade = class_data['Final Grade'][idx]
        semester = class_data['Semester'][idx]
        course_year = class_data['Course Year'][idx]

        if (program_code is None):
            error_list.append(InvalidDataException('Missing Program Code', 
                current_row))
            found_error = True
        elif (program_code not in ('UNDG', 'GRAD')):
            error_list.append(InvalidDataException('Invalid Program Code (Must be either UNDG or GRAD)', 
                current_row))
            found_error = True

        if (subprogram_desc is None):
            error_list.append(InvalidDataException('Missing Subprogram Description', 
                current_row))
            found_error = True
        else: 
            day_regex = r'Day - .*'
            grad_regex = r'Graduate - .*'

            if (re.search(day_regex, subprogram_desc) is None and 
                re.search(grad_regex, subprogram_desc) is None):
                error_list.append(InvalidDataException('Invalid Subprogram Desc.', 
                    current_row))
                found_error = True

        if (course_title is None):
            error_list.append(InvalidDataException('Missing Course Title', 
                    current_row))
            found_error = True
            valid_course_data = False

        if (course_num is None):
            error_list.append(InvalidDataException('Missing Course Number', 
                    current_row))
            found_error = True
            valid_course_data = False

        if (grade is None):
            error_list.append(InvalidDataException('Missing Final Course Grade', 
                    current_row))
            found_error = True
            valid_course_data = False
        else:
            valid_grades = ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 
                'D', 'D-', 'F', 'W', 'P', 'IP')
            if (grade not in valid_grades):
                error_list.append(InvalidDataException('Invalid Final Course Grade', 
                    current_row))
                found_error = True
                valid_course_data = False

        if (semester is None):
            error_list.append(InvalidDataException('Missing Semester', 
                    current_row))
            found_error = True
            valid_course_data = False
        # May need to add Summer courses here?
        elif (semester not in ('FA', 'SP', 'WI')):
            error_list.append(InvalidDataException('Invalid Semester', 
                    current_row))
            found_error = True
            valid_course_data = False

        if (course_year is None):
            error_list.append(InvalidDataException('Missing Course Year', 
                    current_row))
            found_error = True
            valid_course_data = False
        elif (course_year > datetime.now().year):
            error_list.append(InvalidDataException('Invalid Course Year', 
                    current_row))
            found_error = True
            valid_course_data = False

        if (valid_course_data):
            if (random_id is not None):
                course = Course.query.filter_by(course_num=course_num,
                    title=course_title, semester=semester, year=course_year).first()
                if (not course):
                    # Add the course if it does not exist.
                    course = Course(course_num=course_num,
                    title=course_title,
                        semester=semester,
                        year=course_year)
                    db.session.add(course)
                    db.session.flush()

                # Add the new ClassData entry.
                new_class_data = ClassData(student_id=random_id,
                    program_code=program_code,
                    subprogram_desc=subprogram_desc,
                    final_grade=grade,
                    course=course.id)
                db.session.add(new_class_data)
                db.session.flush()
                    

def __insert_students(students: DataFrame):
    '''
    Inserts all students in the students worksheet into the database. Also 
    reports invalid/missing data and inserts the error into the `error_list`.

    param:
        students: The `DataFrame` object representing the students worksheet.

    return:
        A `dict` containing the mapping of the student ID values to a randomized
        ID.
    '''
    id_maps = {}

    # Replace all nans with None.
    students = students.astype(object).where(students.notna(), None)

    # Create datetime objects for the leave date, replace NaTs with None
    students['Leave Date'] = pd.to_datetime(students['Leave Date'])
    students['Leave Date'] = students['Leave Date'].astype(object).where(
        students['Leave Date'].notnull(), None)

    # Replace the first generation student value with a bool.
    students['First Generation Student'] = students['First Generation Student'].map({
        'Y': True, 'y': True, 'Yes': True, 'yes': True, 'True': True, 'T': True,
        't': True, 'true': True, 'N': False, 'n': False, 'No': False, 
        'no': False, 'False': False, 'F': False, 'f': False, 'false': False})

    for idx in students.index:
        found_error = False
        current_row = idx + 2
        if (students['ID'][idx] is None):
            error_list.append(InvalidDataException('Missing ID', current_row))
            found_error = True

        if (students['Last Name'][idx] is None):
            error_list.append(InvalidDataException('Last name missing.', 
                current_row))
            found_error = True

        if (students['First Name'][idx] is None):
            error_list.append(InvalidDataException('Last name missing.', 
                current_row))
            found_error = True

        if (students['Major 1'][idx] is None):
            error_list.append(InvalidDataException('Missing major 1 field. Must have at least 1 major.', 
                current_row))
            found_error = True

        if (students['State Code'][idx] is None):
            error_list.append(InvalidDataException('State Code Missing.', 
                current_row))
            found_error = True

        if (students['Country Code'][idx] is None):
            error_list.append(InvalidDataException('Country code missing', 
                current_row))
            found_error = True

        if (students['Ethnicity'][idx] is None):
            error_list.append(InvalidDataException('Ethnicity missing', 
                current_row))
            found_error = True

        high_school_gpa = students['High School GPA'][idx]
        overall_college_gpa = students['Overall College GPA'][idx]
        major_college_gpa = students['Major College GPA'][idx]
        sat_score = students['SAT Score'][idx]
        act_score = students['ACT Score'][idx]
        leave_date = students['Leave Date'][idx]
        first_gen_student = students['First Generation Student'][idx]
        ethnicity = students['Ethnicity'][idx]
        leave_reason = students['Leave Reason'][idx]

        if (high_school_gpa is not None):
            if (high_school_gpa < 0.0 or high_school_gpa > 4.0):
                error_list.append(InvalidDataException('Invalid High School GPA',
                    current_row))
                found_error = True

        if (overall_college_gpa is not None):
            if (overall_college_gpa < 0.0 or overall_college_gpa > 4.0):
                error_list.append(InvalidDataException('Invalid Overall College GPA',
                    current_row))
                found_error = True

        if (major_college_gpa is not None):
            if (major_college_gpa < 0.0 or major_college_gpa > 4.0):
                error_list.append(InvalidDataException('Invalid Major College GPA',
                    current_row))
                found_error = True

        if (sat_score is not None):
            if (sat_score < app.config['SAT_SCORE_MIN'] or 
                sat_score > app.config['SAT_SCORE_MAX']):
                error_list.append(InvalidDataException('Invalid SAT Score',
                    current_row))
                found_error = True

        if (act_score is not None):
            if (act_score < app.config['ACT_SCORE_MIN'] or 
                act_score > app.config['ACT_SCORE_MAX']):
                error_list.append(InvalidDataException('Invalid ACT Score',
                    current_row))
                found_error = True
                
        if (leave_date is not None):
            if (leave_date > datetime.now()):
                error_list.append(InvalidDataException('Invalid Leave Date',
                    current_row))
                found_error = True

        if (pd.isna(first_gen_student)):
            error_list.append(InvalidDataException('First Generation Student ' + 
                'must be Y/N or T/F', current_row))
            found_error = True

        if (ethnicity is not None):
            if (ethnicity not in ('White', 'Asian', 
                'American Indian or Alaska Native', 'Black or African American',
                'Hispanic or Latino', 'Native Hawaiian or Other Pacific Islander')):
                error_list.append(InvalidDataException('Invalid Ethnicity',
                    current_row))
                found_error = True 

        if (not found_error):
            random_id = Student.gen_random_id()

            # Map the student to the new random id.
            id_maps[students['ID'][idx]] = random_id
            
            new_student = Student(id=random_id, 
                last_name=students['Last Name'][idx],
                first_name=students['First Name'][idx],
                major_1=students['Major 1'][idx],
                major_2=students['Major 2'][idx],
                major_3=students['Major 3'][idx],
                concentration_1=students['Concentration 1'][idx],
                concentration_2=students['Concentration 2'][idx],
                concentration_3=students['Concentration 3'][idx],
                minor_1=students['Minor 1'][idx],
                minor_2=students['Minor 2'][idx],
                minor_3=students['Minor 3'][idx],
                math_placement_score=students['Math Placement Score'][idx],
                high_school_gpa=high_school_gpa,
                overall_college_gpa=overall_college_gpa,
                major_college_gpa=major_college_gpa,
                sat_score=sat_score,
                act_score=act_score,
                state_code=students['State Code'][idx],
                country_code=students['Country Code'][idx],
                leave_date=leave_date,
                first_gen_student=first_gen_student,
                ethnicity=ethnicity,
                leave_reason=leave_reason)

            db.session.add(new_student)
        else:
            failed_students.append(students['ID'][idx])
    
    return id_maps


def __process_errors(errors: list[InvalidDataException]) -> list[dict]:
    '''
    Processes the errors that were found and formats them in a `list` of `dict` 
    objects.

    param: 
        errors: The `list` of errors to process.
    
    return:
        A `list` of `dict` objects that is in a JSON-like format.
    '''
    return [{'error_message': error.message, 'line_num': error.line_num} for error in errors]


