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
from app.models import Student, ClassData, Course, ClassEnum, InvalidClassException
from app import db, app
import re

error_list = []
has_errors = False

# A list of IDs for students that had an error.
failed_students = []

class InvalidDataException(Exception):
    '''
    An exception to hold an invalid data entry.

    param:
        `message`: The error message.
        `line_num`: The line number the error occured on.
        `col_num`: The column number the error occured on.
    '''
    def __init__(self, message, line_num, col_num):
        super().__init__(message)
        self.message = message
        self.line_num = line_num
        self.col_num = col_num
    

    def __repr__(self) -> str:
        return f'{super().__repr__()} at line num: {self.line_num}'

def upload_csv_file(data: FileStorage):
    '''
    Parses the specified csv file and inserts it into the database.

    param: 
        data: The `FileStorage` object containing the csv file.

    return:
        A `Response` object representing the response to be returned to the API
        call.
    '''
    if not data:
        return {'message': 'Unable to read file'}, 400
    else:
        # Split the sheets.
        csv_file = pd.read_csv(data)
        
        # Replace all nan values with None.
        csv_file = csv_file.astype(object).where(csv_file.notna(), None)

        __insert_students(csv_file)
        __insert_class_data(csv_file)

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


def __insert_class_data(csv_file: DataFrame):
    '''
    Inserts all Class Data into the database. Also reports invalid/missing data
    and inserts the error into the `error_list`.

    param:
        class_data: The `DataFrame` object containing the class_data worksheet.
    '''

    def __verify_semester(semester: str) -> bool:
        '''
        Returns a `bool` representing if the semester is valid or not.

        param:
            `semester`: The semester to check.
        return:
            A `bool` representing if the semester is valid or not.
        '''
        return semester in ('FA', 'SP', 'SU', 'WI')

    def __verify_year(year: str) -> bool:
        '''
        Returns a `bool` representing if the year is valid or not.

        param:
            `year`: The year to verify.
        return:
            A `bool` representing if the year is valid or not.
        '''
        return (int(year) <= datetime.now().year)

    def __insert_course(semester: str, year: str, num_term_code: str, 
        course_id: str) -> int:
        '''
        Searches for the course matching the given data. If the course is found,
        the ID of it is returned. If it does not exist, it is created and the 
        id is return.

        param:
            `semester`: A `str` holding the semester.
            `year`: A `str` holding the year.
            `num_term_code`: A `str` holding the term numeric code.
            `course_id`: A `str` holding the course ID.
        return:
            The ID of the `Course` object.
        '''
        course_obj = Course.query.filter(Course.term_code==num_term_code and 
            Course.course_num==course_id and Course.semester==semester and 
            Course.year==year).first()

        # If the course already exists, return the ID of it.
        if (course_obj):
            return course_obj.id
        else:
            # If the course does not exist, create it and add it to the database.
            new_course = Course(term_code=num_term_code, course_num=course_id,
                semester=semester, year=year)
            db.session.add(new_course)
            db.session.flush()
            return new_course.id
        
    for idx in csv_file.index:
        current_row = idx + 2
        found_error = False
        valid_course_data = True

        student_id = csv_file['Unique_ID'][idx]
        term = csv_file['Term'][idx]
        num_term_code = csv_file['Numeric_Term_Code'][idx]
        program_level = csv_file['Program_Level'][idx]
        subprogram_code = csv_file['Subprogram_Code'][idx]
        course_id = csv_file['Course_Number'][idx]
        grade = csv_file['Course_Grade'][idx]

        if (term is None):
            error_list.append(InvalidDataException('Missing Term', current_row, 5))
            found_error = True
            valid_course_data = False
        else:
            split_term = term.split(' ')
            if (len(split_term) != 2):
                error_list.append(InvalidDataException('Invalid Term', 
                    current_row, 5))
                found_error = True
                valid_course_data = False
            else:
                # Verify the semester.
                if (__verify_semester(split_term[0])):
                    semester = split_term[0]
                else:
                    error_list.append(InvalidDataException('Invalid Semester', 
                        current_row, 5))
                    found_error = True
                    valid_course_data = False
                
                # Verify the year.
                if (__verify_year(split_term[1])):
                    year = split_term[1]
                else:
                    error_list.append(InvalidDataException('Invalid Year', 
                        current_row, 5))
                    found_error = True
                    valid_course_data = False

        if (num_term_code is None): 
            error_list.append(InvalidDataException('Numeric term missing.', 
                current_row, 6))
            found_error = True
            valid_course_data = False

        if (course_id is None):
            error_list.append(InvalidDataException('Course number missing.', 
                current_row, 34))
            found_error = True 
            valid_course_data = False

        course = None
        # If the course data was all valid, get the course ID.
        if (valid_course_data):
            course = __insert_course(semester, year, num_term_code, course_id)

        if (program_level is None):
            error_list.append(InvalidDataException('Missing Program Level', 
                current_row, 7))
            found_error = True
        elif (program_level not in ('UNDG', 'GRAD')):
            error_list.append(InvalidDataException('Invalid Program Level (Must be either UNDG or GRAD)', 
                current_row, 7))
            found_error = True

        if (subprogram_code is None):
            error_list.append(InvalidDataException('Missing Subprogram Code', 
                current_row, 8))
            found_error = True

        if (grade is None):
            error_list.append(InvalidDataException('Missing Course Grade', 
                    current_row, 35))
            found_error = True
            valid_course_data = False
        else:
            valid_grades = ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 
                'D', 'D-', 'F', 'W', 'P', 'IP')
            if (grade not in valid_grades):
                error_list.append(InvalidDataException('Invalid Course Grade', 
                    current_row))
                found_error = True
                valid_course_data = False

        if (student_id is None):
            error_list.append(InvalidDataException('Missing Unique_ID', 
                    current_row, 1))
            found_error = True

        if (course and not found_error):
            # Add the new ClassData entry.
            new_class_data = ClassData(student_id=student_id,
                program_level=program_level,
                subprogram_code=subprogram_code,
                grade=grade,
                course=course)
            db.session.add(new_class_data)
            db.session.flush()
                    

def __insert_students(csv_file: DataFrame):
    '''
    Inserts all students into the database. Also reports invalid/missing data 
    and inserts the error into the `error_list`.

    param:
        csv_file: The `DataFrame` object representing the data.
    '''
    for idx in csv_file.index:
        found_error = False
        current_row = idx + 2

        # Check to see if the Student has already been added.
        unique_id = csv_file['Unique_ID'][idx]
        if (unique_id is None):
            error_list.append(InvalidDataException('Unique ID missing.', 
                current_row))
            found_error = True
        else:
            # If the student exists, move to the next row of the data.
            if Student.query.get(unique_id):
                continue
        
        admit_year = csv_file['Admit_Year'][idx]
        admit_term = csv_file['Admit_Term'][idx]
        admit_type = csv_file['Admit_Type'][idx]
        major_1_code = csv_file['Major1_Code'][idx]
        major_1_desc = csv_file['Major1_Desc'][idx]
        major_2_code = csv_file['Major2_Code'][idx]
        major_2_desc = csv_file['Major2_Desc'][idx]
        minor_1_code = csv_file['Minor1_Code'][idx]
        minor_1_desc = csv_file['Minor1_Desc'][idx]
        concentration_code = csv_file['Concentration_Code'][idx]
        concentration_desc = csv_file['Concentration_Desc'][idx]
        class_year = csv_file['Class'][idx]
        city = csv_file['City'][idx]
        state = csv_file['State'][idx]
        postal_code = csv_file['Postal_Code'][idx]
        country = csv_file['Country_Code'][idx]
        race_ethnicity = csv_file['Race-Ethnicity'][idx]
        gender = csv_file['Sex'][idx]
        gpa_cumulative = csv_file['GPA_Cum'][idx]
        sat_math = csv_file['SAT_Math'][idx]
        sat_total = csv_file['SAT_Total'][idx]
        act_score = csv_file['ACT_Score'][idx]
        math_placement_score = csv_file['Math_Placement'][idx]
        hs_gpa = csv_file['HS_GPA'][idx]
        hs_ceeb = csv_file['HS_CEEB'][idx]
        hs_name = csv_file['HS_Name'][idx]
        hs_city = csv_file['HS_City'][idx]
        hs_state = csv_file['HS_State'][idx]
        cohort = csv_file['Cohort'][idx]

        if (admit_year is None):
            error_list.append(InvalidDataException('Admit year missing.', 
                current_row, 2))
            found_error = True

        if (admit_term is None):
            error_list.append(InvalidDataException('Admit term missing.', 
                current_row, 3))
            found_error = True

        if (admit_type is None):
            error_list.append(InvalidDataException('Admit type missing.', 
                current_row, 4))
            found_error = True

        if (major_1_code is None):
            error_list.append(InvalidDataException('Major1_Code missing.', 
                current_row, 9))
            found_error = True

        if (major_1_desc is None):
            error_list.append(InvalidDataException('Major1_Desc missing.', 
                current_row, 10))
            found_error = True

        # Try to parse the class year if it exists, reporting a failed parse.
        if (class_year is None):
            error_list.append(InvalidDataException('Class missing.', 
                current_row, 17))
            found_error = True
        else:
            try:
                class_year = ClassEnum.parse_class(class_year)
            except InvalidClassException:
                error_list.append(InvalidDataException('Invalid Class', 
                    current_row, 17))
                found_error = True

        if (city is None):
            error_list.append(InvalidDataException('City missing.', 
                current_row, 18))
            found_error = True

        if (postal_code is None):
            error_list.append(InvalidDataException('Postal_Code missing.', 
                current_row, 19))
            found_error = True

        if (country is None):
            error_list.append(InvalidDataException('Country_Code missing.', 
                current_row, 20))
            found_error = True

        if (race_ethnicity is None):
            error_list.append(InvalidDataException('Race-Ethnicity missing.', 
                current_row, 21))
            found_error = True
        
        if (gender is None):
            error_list.append(InvalidDataException('Sex missing.', 
                current_row, 22))
            found_error = True

        if (gpa_cumulative is None):
            gpa_cumulative = 0.00

        if (not found_error):
            new_student = Student(id=unique_id,
                admit_year=admit_year,
                admit_term=admit_term,
                admit_type=admit_type,
                major_1=major_1_code,
                major_1_desc=major_1_desc,
                major_2=major_2_code,
                major_2_desc=major_2_desc,
                minor_1=minor_1_code,
                minor_1_desc=minor_1_desc,
                concentration_code=concentration_code,
                concentration_desc=concentration_desc,
                class_year=class_year,
                city=city,
                state=state,
                country=country,
                postal_code=postal_code,
                math_placement_score=math_placement_score,
                race_ethnicity=race_ethnicity,
                gender=gender,
                gpa_cumulative=gpa_cumulative,
                high_school_gpa=hs_gpa,
                sat_math=sat_math,
                sat_total=sat_total,
                act_score=act_score,
                high_school_name=hs_name,
                high_school_city=hs_city,
                high_school_state=hs_state,
                high_school_ceeb=hs_ceeb,
                cohort=cohort
            )
            db.session.add(new_student)


def __process_errors(errors: list[InvalidDataException]) -> list[dict]:
    '''
    Processes the errors that were found and formats them in a `list` of `dict` 
    objects.

    param: 
        errors: The `list` of errors to process.
    
    return:
        A `list` of `dict` objects that is in a JSON-like format.
    '''
    return [{
        'error_message': error.message, 'line_num': error.line_num, 
        'col_num': error.col_num
    } for error in errors]


