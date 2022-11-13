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

function logout(evt) {
    evt.preventDefault();
    fetch('/logout', {method: 'POST'}).then((res) => {
        if (res.redirected) {
            window.location.href = res.url;
        }
    });
}

let currentDropdownID = 0;
let classSemesterMap;

window.onload = () => {
    fetch('/course-semester-mapping')
        .then((res) => res.json())
        .then((data) => {
            classSemesterMap = data;
            // Add 2 dropdowns for courses.
            addNewCourseDropdowns(false);
            addNewCourseDropdowns(false);
    });
}

/**
 * Removes the row with the specified ID from the courseDropdownDiv.
 * 
 * @param {Number} rowID The ID of the row that is being removed.
 */
function removeCourseDropdownRow(rowID) {
    document.getElementById(rowID).remove();
}


function addCorrespondingCourseSemesters(courseSelect, selectID) {
    var selectElement = document.getElementById(selectID);
    var selectedCourse = courseSelect.options[courseSelect.selectedIndex].text;

    selectElement.innerHTML = '<option selected disabled>Choose a semester...</option>'

    for (var semester of classSemesterMap[selectedCourse]) {
        selectElement.innerHTML += `<option value="${semester}">${semester}</option>\n`;
    }
}

/**
 * Adds a new set of dropdown boxes for a course to the courseDropdownsDiv.
 */
function addNewCourseDropdowns(addDeleteButton) {
    var dropdownsDiv = document.getElementById('courseDropdownDiv');

    // Increment the ID counter for the new row.
    currentDropdownID++;

    var options = '';
    // Build the list of options for the course codes.
    for (var key in classSemesterMap) {
        options += `<option value="${key}">${key}</option>\n`;
    }

    if (addDeleteButton) {
        var buttonStr = `<button class="h-25 col-2 btn btn-danger" onclick='removeCourseDropdownRow("row-${currentDropdownID}")'>Remove</button>`;
    } else {
        var buttonStr = '';
    }
    // Build the row, adding every course code.
    var row = `
        <div class="row align-items-center align-middle mb-4" id="row-${currentDropdownID}">
            <div class="col-4">
                <h6>Select course...</h6>
                <select class="form-select" id="course-${currentDropdownID}" onchange="addCorrespondingCourseSemesters(this, 'semester-${currentDropdownID}'); checkDropdowns();">
                    <option selected disabled>Choose a course...</option>
                    ${options}
                </select>
            </div> 
            <div class='col-5' style="margin-left: 10px;">
                <h6>Select semester...</h6>
                <select class="form-select" id="semester-${currentDropdownID}" onchange="checkDropdowns();">
                    <option selected disabled>Choose a semester...</option>
                </select>
            </div>
            ${buttonStr}
        </div>
    `;
    dropdownsDiv.innerHTML += row;
    dropdownsDiv.scrollTop = dropdownsDiv.scrollHeight;
    document.getElementById('showChartGraphButton').disabled = true;
}

function checkDropdowns() {
    function hasValidSelection(selectElement) {
        return selectElement.selectedIndex != 0;
    }

    var validDropdowns = true;
    for (var i = 1; i <= currentDropdownID; i++) {
        var courseSelect = document.getElementById(`course-${i}`);
        var semesterSelect = document.getElementById(`semester-${i}`);

        if (courseSelect != null && semesterSelect != null) {
            validDropdowns = validDropdowns && (hasValidSelection(courseSelect) &&
                hasValidSelection(semesterSelect));
        }
    }

    if (validDropdowns) {
        document.getElementById('showChartGraphButton').disabled = false;
    } else {
        document.getElementById('showChartGraphButton').disabled = true;
    }
}

function getSelectedCourseData() {
    function getSelectedValue(selectElement) {
        return selectElement.options[selectElement.selectedIndex].text;
    }

    var selectedCourses = {};
    for (var i = 1; i <= currentDropdownID; i++) {
        var selectedCourse = getSelectedValue(document
                .getElementById(`course-${i}`));
        var selectedSemester = getSelectedValue(document
                .getElementById(`semester-${i}`));

        if (selectedCourse != null && selectedSemester != null){
            selectedCourses[selectedCourse] = selectedSemester;
        }
    }
}