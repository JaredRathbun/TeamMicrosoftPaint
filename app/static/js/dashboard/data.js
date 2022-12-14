/*
* Copyright (c) 2022 Jared Rathbun and Katie O'Neil. 
*
* This file is part of STEM Data Dashboard.
*
* STEM Data Dashboard is free software: you can redistribute it and/or modify it
* under the terms of the GNU General Public License as published by the Free 
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
* This Source Code Form is subject to the terms of the Mozilla Public
* License, v. 2.0. If a copy of the MPL was not distributed with this
* file, You can obtain one at https://mozilla.org/MPL/2.0/.
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
                $(id).slideToggle('slow', () => { });
            }
        });
    });
};

function logout(evt) {
    evt.preventDefault();
    fetch('/logout', { method: 'POST' }).then((res) => {
        if (res.redirected) {
            window.location.href = res.url;
        }
    });
}

var tableData = null, sortedTableData = null, dataLoaded = false;
window.onload = () => {
    fetch('/all-data').then((res) => res.json()).then((data) => {
        tableData = data;
        sortedTableData = data.sort((val1, val2) => val1['student_id']
            .localeCompare(val2['student_id']));
        dataLoaded = true;
        createTable(data);
    });
};

function createTable(data) {
    document.getElementById('dataTable').innerHTML = '';
    const convertToNA = (val) => (val == null) ? 'N/A' : val;
    const convertBooleanToString = (val) => (val) ? 'Yes' : 'No';
    let rowID = 0;
    let bodyString = '';
    for (const val of data) {
        const row = `
            <tr class="d-flex">
                <td class="col-1">
                    <i class="fa-solid fa-eye-slash rowToggle" data-collapse-target="row-${rowID}"></i>
                </td>
                <td class="col-2">${val.student_id}</td>
                <td class="col-2">${val.course_code}</td>
                <td class="col-2">${val.program_level}</td>
                <td class="col-2">${val.subprogram_code}</td>
                <td class="col-1">${val.semester}</td>
                <td class="col-1">${val.year}</td>
                <td class="col-1">${val.grade}</td>
            </tr>
            <tr class="d-flex">
                <td hidden id="row-${rowID}">
                    <div class="container mx-2 mt-1">
                        <div class="row">
                            <div class="col-4">
                                <h5 class="mx-2">Student Demographics</h5>
                                <table class="table my-0 col-4">
                                    <tr>
                                        <th>Gender</th>
                                        <td>${val.demographics.gender}</td>
                                    </tr>
                                    <tr>
                                        <th>Race/Ethnicity</th>
                                        <td>${val.demographics.race_ethnicity}</td>
                                    </tr>
                                    <tr>
                                        <th>Home Location</th>
                                        <td>${val.demographics.home_location}</td>
                                    </tr>
                                    <tr>
                                        <th>Home Zip Code</th>
                                        <td>${val.demographics.home_zip_code}</td>
                                    </tr>
                                    <tr>
                                        <th>High School Name</th>
                                        <td>${val.demographics.high_school_name}</td>
                                    </tr>
                                    <tr>
                                        <th>High School Location</th>
                                        <td>${val.demographics.high_school_location}</td> 
                                    </tr>
                                    <tr>
                                        <th>High School CEEB</th>
                                        <td>${val.demographics.high_school_ceeb}</td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-4">
                                <h5 class="mx-3">Student Academic Information</h5>
                                <table class="table my-0 col-4">
                                    <tr>
                                        <th>Major 1</th>
                                        <td>${val.academic_info.major_1}</td>
                                    </tr>
                                    <tr>
                                        <th>Major 2</th>
                                        <td>${val.academic_info.major_2}</td>
                                    </tr>
                                    <tr>
                                        <th>Minor</th>
                                        <td>${val.academic_info.minor_1}</td>
                                    </tr>
                                    <tr>
                                        <th>Concentration</th>
                                        <td>${val.academic_info.concentration}</td>
                                    </tr>
                                    <tr>
                                        <th>Class</th>
                                        <td>${val.academic_info.class_year}</td>
                                    </tr>
                                    <tr>
                                        <th>Admit Term + Year</th>
                                        <td>${val.academic_info.admit_term_year}</td>
                                    </tr>
                                    <tr>
                                        <th>Admit Type</th>
                                        <td>${val.academic_info.admit_type}</td>
                                    </tr>
                                    <tr>
                                        <th>Cohort</th>
                                        <td>${val.academic_info.cohort}</td>
                                    </tr>
                                </table>
                            </div>
                            <div class="col-4">
                                <h5 class="mx-2">Student Academic Scores</h5>
                                <table class="table my-0 col-4">
                                    <tr>
                                        <th>Cumulative College GPA</th>
                                        <td>${val.academic_scores.college_gpa}</td>
                                    </tr>
                                    <tr>
                                        <th>Math Placement Score</th>
                                        <td>${val.academic_scores.math_placement_score}</td>
                                    </tr>
                                    <tr>
                                        <th>SAT Total Score</th>
                                        <td>${val.academic_scores.sat_total}</td>
                                    </tr>
                                    <tr>
                                        <th>SAT Math Score</th>
                                        <td>${val.academic_scores.sat_math}</td>
                                    </tr>
                                    <tr>
                                        <th>ACT Score</th>
                                        <td>${val.academic_scores.act_score}</td>
                                    </tr>
                                    <tr>
                                        <th>High School GPA</th>
                                        <td>${val.academic_scores.high_school_gpa}</td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </td>
            </tr> 
        `;
        bodyString += row;
        // document.getElementById('tablebody').innerHTML += row;
        rowID++;
    }

    let tableString = `
        <table class="table table-responsive table-striped my-0">
            <thead>
                <tr class="d-flex sticky-header" style="position: sticky;">
                    <th class="col-1"></th>
                    <th class="col-2">Student ID #</th>
                    <th class="col-2">Course Code</th>
                    <th class="col-2">Program Level</th>
                    <th class="col-2">Subprogram Code</th>
                    <th class="col-1">Semester</th>
                    <th class="col-1">Year</th>
                    <th class="col-1">Final Grade</th>
                </tr>
            </thead>
            <tbody id="tablebody">
                ${bodyString}
            </tbody>
        </table>
    `;
    document.getElementById('dataTable').innerHTML = tableString;

    applyShowHideToggle();
}

function searchForData(searchElement) {
    if (dataLoaded) {
        const searchVal = searchElement.value;
        
        if (searchVal != '') {
            var start, end;
            for (var i = 0; i < sortedTableData.length; i++) {
                if (sortedTableData[i].student_id == searchVal) {
                    if (start == undefined) {
                        start = i;
                    } else {
                        end = i;
                    }
                }
            }

            if (start != undefined && end != undefined) {
                var copy = sortedTableData;
                createTable(copy.splice(start, end + 1));
            }
        } else {
            createTable(tableData);
        }
    }

}

/**
 * Sorts the data array using merge sort. Offers a running time of O(nlgn).
 * 
 * @param {Array} data The array of data to sort. 
 * @param {String} key The key to sort by in the list of objects.
 * 
 * @return The list in the sorted format.
 */
// function sort(data, key = 'student_id') {

//     function merge(left, right) {
//         let resArray = [], leftIdx = 0, rightIdx = 0;

//         // We will concatenate values into the resultArray in order
//         while (leftIdx < left.length && rightIdx < right.length) {
//             if (left[leftIdx][key].localeCompare(right[rightIdx][key])) {
//                 resArray.push(left[leftIdx]);
//                 leftIdx++; // move left array cursor
//             } else {
//                 resArray.push(right[rightIdx]);
//                 rightIdx++; // move right array cursor
//             }
//         }

//         // We need to concat here because there will be one element remaining
//         // from either left OR the right
//         return resArray.concat(left.slice(leftIdx))
//             .concat(right.slice(rightIdx));
//     }

//     const data_len = data.length;

//     if (data_len <= 1) {
//         return data;
//     }

//     const mid = Math.floor(data_len / 2);
//     const left = data.splice(0, mid), right = data.splice(mid);

//     return merge(sort(left), sort(right));
// }   