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

    def __insert_course(semester: str, year: str, section: str, 
        num_term_code: str, course_id: str, course_title: str) -> int:
        '''
        Searches for the course matching the given data. If the course is found,
        the ID of it is returned. If it does not exist, it is created and the 
        id is return.

        param:
            `semester`: A `str` holding the semester.
            `year`: A `str` holding the year.
            `section`: A `str` holding the section.
            `term_code`: A `str` holding the term numeric code.
            `course_num`: A `str` holding the course number.
            `course_title`: A `str` holding the course title.
        return:
            The ID of the `Course` object.
        '''
        course_obj = Course.query.filter(Course.term_code==num_term_code, 
            Course.course_num==course_id, Course.semester==semester, 
            Course.year==year, Course.section == section, 
            Course.title == course_title).first()

        # If the course already exists, return the ID of it.
        if (course_obj):
            return course_obj.id
        else:
            # If the course does not exist, create it and add it to the database.
            new_course = Course(term_code=num_term_code, course_num=course_id,
                section=section, semester=semester, year=year, 
                title=course_title)
            db.session.add(new_course)
            db.session.flush()
            return new_course.id
        
    for idx in csv_file.index:
        current_row = idx + 2
        found_error = False
        valid_course_data = True

        student_id = csv_file['Unique_ID'][idx]
        semester = csv_file['Course_Term'][idx]
        term_code = csv_file['Term_Code'][idx]
        section = csv_file['Course_Section'][idx]
        year = csv_file['Course_Year'][idx]
        course_num = csv_file['Course_Number'][idx]
        grade = csv_file['Course_Grade'][idx]
        course_title = csv_file['Course_Title'][idx]

        if (student_id is None):
            error_list.append(InvalidDataException('Missing Unique_ID', 
                current_row, 1))
            found_error = True
            valid_course_data = False

        if (semester is None):
            error_list.append(InvalidDataException('Missing Course_Term', 
                current_row, 33))
            found_error = True
            valid_course_data = False

        if (term_code is None):
            error_list.append(InvalidDataException('Missing Term_Code', 
                current_row, 34))
            found_error = True
            valid_course_data = False

        if (section is None):
            error_list.append(InvalidDataException('Missing Course_Section', 
                current_row, 35))
            found_error = True
            valid_course_data = False

        if (year is None):
            error_list.append(InvalidDataException('Missing Course_Year', 
                current_row, 32))
            found_error = True
            valid_course_data = False

        if (course_num is None):
            error_list.append(InvalidDataException('Missing Course_Number', 
                current_row, 30))
            found_error = True
            valid_course_data = False
        else:
            if (len(course_num) < 7 or len(course_num) > 9):
                error_list.append(InvalidDataException('Invalid Course Number', 
                    current_row, 30))
                found_error = True
                valid_course_data = False

        # if (grade is None):
        #     error_list.append(InvalidDataException('Missing Grade', current_row,
        #         36))
        #     found_error = True
        #     valid_course_data = False

        if (course_title is None):
            error_list.append(InvalidDataException('Missing Course_Title', 
                current_row, 35))
            found_error = True
            valid_course_data = False

        course = None
        # If the course data was all valid, get the course ID.
        if (valid_course_data):
            course = __insert_course(semester, year, section, term_code, 
                course_num, course_title)

        if (course and not found_error):
            # Add the new ClassData entry.
            new_class_data = ClassData(student_id=student_id,
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
        major_1 = csv_file['Major_1'][idx]
        major_1_desc = csv_file['Major_1_Desc'][idx]
        major_2 = csv_file['Major_2'][idx]
        major_2_desc = csv_file['Major_2_Desc'][idx]
        concentration = csv_file['Major_1_Conc'][idx]
        minor_1 = csv_file['Minor_1'][idx]
        minor_1_desc = csv_file['Minor_1_Desc'][idx]
        class_year = csv_file['Class'][idx]
        city = csv_file['City'][idx]
        state = csv_file['State'][idx]
        country = csv_file['Country'][idx]
        race = csv_file['Race'][idx]
        sex = csv_file['Sex'][idx]
        first_gen_student = csv_file['First_Gen?'][idx]
        accuplacer_score = csv_file['Accuplacer_Score'][idx]
        college_gpa = csv_file['College_GPA'][idx]
        sat_math = csv_file['SAT_Math'][idx]
        math_placement_score = csv_file['Math_Placement_Score'][idx]
        hs_gpa = csv_file['HS_GPA'][idx]
        hs_name = csv_file['HS_Name'][idx]
        hs_city = csv_file['HS_City'][idx]
        hs_state = csv_file['HS_State'][idx]
        is_honors = csv_file['Honors?'][idx]
        is_compass = csv_file['Compass?'][idx]
        is_austin = csv_file['Austin?'][idx]
        is_athlete = csv_file['Athlete?'][idx]

        if (sex is None):
            error_list.append(InvalidDataException('Sex missing.', 
                current_row, 2))
            found_error = True
        elif (sex not in ('M', 'F', 'UN')):
            error_list.append(InvalidDataException('Invalid sex.', 
                current_row, 2))
            found_error = True

        if (race not in ('BL', 'WH', 'UN', 'HISP', 'MU', 'NO', 'AS', 'AM', 'IS')):
            print(race)

        if (race is None):
            error_list.append(InvalidDataException('Race missing.', 
                current_row, 3))
            found_error = True
        elif (race not in ('BL', 'WH', 'UN', 'HISP', 'MU', 'NO', 'AS', 'AM', 'IS')):
            error_list.append(InvalidDataException('Invalid race.', 
                current_row, 3))
            found_error = True

        if (admit_year is None):
            error_list.append(InvalidDataException('Admit year missing.', 
                current_row, 4))
            found_error = True
        else:
            if (admit_year == '0'):
                admit_year = None

        if (admit_term is None):
            error_list.append(InvalidDataException('Admit term missing.', 
                current_row, 5))
            found_error = True
        elif (admit_term not in ('FA', 'SP', 'SU', 'WI', 'UN')):
            error_list.append(InvalidDataException('Invalid admit term.', 
                current_row, 5))
            found_error = True

        if (country is None):
            error_list.append(InvalidDataException('Country missing.', 
                current_row, 13))
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
                    current_row, 14))
                found_error = True

        if (first_gen_student is None):
            error_list.append(InvalidDataException('First gen student missing.', 
                current_row, 15))
            found_error = True
        elif (first_gen_student not in ('Y', 'N')):
            error_list.append(InvalidDataException('Invalid First gen student.', 
                current_row, 15))
            found_error = True
        else:
            first_gen_student = (first_gen_student == 'Y')

        if (hs_name is None):
            error_list.append(InvalidDataException('High school name missing.', 
                current_row, 17))
            found_error = True

        if (hs_city is None):
            error_list.append(InvalidDataException('High school city missing.', 
                current_row, 18))
            found_error = True
        
        if (hs_state is None):
            error_list.append(InvalidDataException('High school state missing.', 
                current_row, 19))
            found_error = True

        if (is_honors is None):
            error_list.append(InvalidDataException('Honors? missing.', 
                current_row, 20))
            found_error = True
        elif (is_honors not in ('N', 'Y')):
            error_list.append(InvalidDataException('Invalid Honors?.', 
                current_row, 20))
            found_error = True
        else:
            is_honors = (is_honors == 'Y')

        if (is_compass is None):
            error_list.append(InvalidDataException('Compass? missing.', 
                current_row, 21))
            found_error = True
        elif (is_compass not in ('N', 'Y')):
            error_list.append(InvalidDataException('Invalid Compass?.', 
                current_row, 21))
            found_error = True
        else:
            is_compass = (is_compass == 'Y')

        if (is_austin is None):
            error_list.append(InvalidDataException('Austin? missing.', 
                current_row, 22))
            found_error = True
        elif (is_austin not in ('N', 'Y')):
            error_list.append(InvalidDataException('Invalid Austin?.', 
                current_row, 22))
            found_error = True
        else:
            is_austin = (is_austin == 'Y')

        if (is_athlete is None):
            error_list.append(InvalidDataException('Athlete? missing.', 
                current_row, 23))
            found_error = True
        elif (is_athlete not in ('N', 'Y')):
            error_list.append(InvalidDataException('Invalid Athlete?.', 
                current_row, 23))
            found_error = True
        else:
            is_athlete = (is_athlete == 'Y')

        if (not found_error):
            new_student = Student(id=unique_id,
                admit_year=admit_year,
                admit_term=admit_term,
                major_1=major_1,
                major_1_desc=major_1_desc,
                major_2=major_2,
                major_2_desc=major_2_desc,
                minor_1=minor_1,
                minor_1_desc=minor_1_desc,
                concentration=concentration,
                class_year=class_year,
                city=city,
                state=state,
                country=country,
                race=race,
                sex=sex,
                first_gen_student=first_gen_student,
                accuplacer_score=accuplacer_score,
                college_gpa=college_gpa,
                sat_math=sat_math,
                math_placement_score=math_placement_score,
                hs_gpa=hs_gpa,
                hs_name=hs_name,
                hs_city=hs_city,
                hs_state=hs_state,
                is_honors=is_honors,
                is_compass=is_compass,
                is_austin=is_austin,
                is_athlete=is_athlete
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