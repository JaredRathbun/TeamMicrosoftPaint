/*
* Copyright (c) 2022 Jared Rathbun and Katie O'Neil. 
*
* This file is part of STEM Data Dashboard.
*
* STEM Data Dashboard is free software: you can redistribute it and/or modify 
* it under the terms of the GNU General Public License as published by the Free 
* Software Foundation, either version 3 of the License, or (at your option) any 
* later version.
*
* STEM Data Dashboard is distributed in the hope that it will be useful, but 
* WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
* FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more 
* details.
*
* You should have received a copy of the GNU General Public License along with 
* STEM Data Dashboard. If not, see <https://www.gnu.org/licenses/>.
*
*/

const applyShowHideToggle = () => {
    $(() => {
        // Hide all tables that are sub tables.

        $('.rowToggle').click((evt) => {
            evt.stopPropagation();
            let tgt = $(evt.target).data('collapse-target');
            let icon = $(evt.target);

            // Flip the eye icon.
            if (icon.hasClass('fa-eye-slash')) {
                icon.removeClass('fa-eye-slash').addClass('fa-eye');
            } else {
                icon.removeClass('fa-eye').addClass('fa-eye-slash');
            }

            var id = '#' + tgt;
            if (!$(id).is(':visible')) {
                $(id).removeAttr('hidden');
                $(id).slideDown(400);
            } else {
                $(id).slideToggle('slow', () => {});
            }
        });
    });
};

function logout(evt) {
    evt.preventDefault();
    fetch('/logout', {method: 'POST'}).then((res) => {
        if (res.redirected) {
            window.location.href = res.url;
        }
    });
}

window.onload = () => {
    fetch('/all-data').then((res) => res.json()).then((data) => {
        createTable(data);
    });
};

function createTable(data) {
    const convertToNA = (val) => (val == null) ? 'N/A' : val;
    const convertBooleanToString = (val) => (val) ? 'Yes' : 'No';

    let rowID = 0;
    for (const val of data) {
        const row = `
            <tr class="d-flex">
                <td class="col-1">
                    <i class="fa-solid fa-eye-slash rowToggle" data-collapse-target="row-${rowID}"></i>
                </td>
                <td class="col-2">${val.student_id}</td>
                <td class="col-2">${val.course_code}</td>
                <td class="col-2">${val.subprogram_desc}</td>
                <td class="col-2">${val.course_title}</td>
                <td class="col-1">${val.semester}</td>
                <td class="col-1">${val.year}</td>
                <td class="col-1">${val.final_grade}</td>
            </tr>
            <tr class="d-flex">
                <td hidden id="row-${rowID}">
                    <div class="container mx-2 mt-1">
                        <div class="row">
                            <div class="col-4">
                                <h5 class="mx-2">Student Demographics</h5>
                                <table class="table my-0 col-4">
                                    <tr>
                                        <th>First Name</th>
                                        <td>${val.demographics.first_name}</td>
                                    </tr>
                                    <tr>
                                        <th>Last Name</th>
                                        <td>${val.demographics.last_name}</td>
                                    </tr>
                                    <tr>
                                        <th>Major 1</th>
                                        <td>${val.demographics.major_1}</td>
                                    </tr>
                                    <tr>
                                        <th>Major 2</th>
                                        <td>${convertToNA(val.demographics.major_2)}</td>
                                    </tr>
                                    <tr>
                                        <th>Major 3</th>
                                        <td>${convertToNA(val.demographics.major_3)}</td>
                                    </tr>
                                    <tr>
                                        <th>Minor 1</th>
                                        <td>${convertToNA(val.demographics.minor_1)}</td>
                                    </tr>
                                    <tr>
                                        <th>Minor 2</th>
                                        <td>${convertToNA(val.demographics.minor_2)}</td>
                                    </tr>
                                    <tr>
                                        <th>Minor 3</th>
                                        <td>${convertToNA(val.demographics.minor_3)}</td>
                                    </tr>
                                    <tr>
                                        <th>Ethnicity</th>
                                        <td>${val.demographics.ethnicity}</td>
                                    </tr>
                                    <tr>
                                        <th>Home Location</th>
                                        <td>${val.demographics.home_location}</td>
                                    </tr>
                                    <tr>
                                        <th>First Generation Student</th>
                                        <td>${convertBooleanToString(val.demographics.first_gen_student)}</td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-4">
                                <h5 class="mx-2">Student Academic Information</h5>
                                <table class="table my-0 col-4">
                                    <tr>
                                        <th>Overall College GPA</th>
                                        <td>${val.academic_info.overall_college_gpa}</td>
                                    </tr>
                                    <tr>
                                        <th>Major College GPA</th>
                                        <td>${val.academic_info.major_college_gpa}</td>
                                    </tr>
                                    <tr>
                                        <th>High School GPA</th>
                                        <td>${val.academic_info.high_school_gpa}</td>
                                    </tr>
                                    <tr>
                                        <th>Math Placement Score</th>
                                        <td>${val.academic_info.math_placement_score}</td>
                                    </tr>
                                    <tr>
                                        <th>SAT Score</th>
                                        <td>${convertToNA(val.academic_info.sat_score)}</td>
                                    </tr>
                                    <tr>
                                        <th>ACT Score</th>
                                        <td>${convertToNA(val.academic_info.act_score)}</td>
                                    </tr>
                                    <tr>
                                        <th>Leave Date</th>
                                        <td>${convertToNA(val.academic_info.leave_date)}</td>
                                    </tr>
                                    <tr>
                                        <th>Leave Reason</th>
                                        <td>${convertToNA(val.academic_info.leave_reason)}</td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-4">
                                <h5 class="mx-2">Student MCAS Scores</h5>
                                <table class="table my-0 col-4">
                                    <thead>
                                        <tr>
                                            <th>MCAS Subject</th>
                                            <th>RAW Score</th>
                                            <th>Scaled Score</th>
                                            <th>Achievement Level</th>
                                        </tr>
                                        <tbody>
                                            <tr>
                                                <td>English</td>
                                                <td>${convertToNA(val.mcas_info.english_raw)}</td>
                                                <td>${convertToNA(val.mcas_info.english_scaled)}</td>
                                                <td>${convertToNA(val.mcas_info.english_achievement_level)}</td>
                                            </tr>
                                            <tr>
                                                <td>Math</td>
                                                <td>${convertToNA(val.mcas_info.math_raw)}</td>
                                                <td>${convertToNA(val.mcas_info.math_scaled)}</td>
                                                <td>${convertToNA(val.mcas_info.math_achievement_level)}</td>
                                            </tr>
                                            <tr>
                                                <td>STEM</td>
                                                <td>${convertToNA(val.mcas_info.stem_raw)}</td>
                                                <td>${convertToNA(val.mcas_info.stem_scaled)}</td>
                                                <td>${convertToNA(val.mcas_info.stem_achievement_level)}</td>
                                            </tr>
                                        </tbody>
                                    </thead>
                                </table>
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
        `;
        console.log(document.getElementById('tablebody').innerHTML);
        document.getElementById('tablebody').innerHTML += row;
        rowID++;
    }

    applyShowHideToggle();
}