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
window.jsPDF = window.jspdf.jsPDF;

alertify.defaults.transition = "slide";
alertify.defaults.theme.ok = "btn btn-primary";
alertify.defaults.theme.cancel = "btn btn-danger";
alertify.defaults.theme.input = "form-control";

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

// A map for the types of graphs that can be generated for each column in the 
// data.
const columnChartGraphMap = {
    'avg_gpa': ['Bar Graph'],
    'gpa_cumulative': ['Scatterplot'],
    'avg_high_school_gpa': ['Bar Graph'],
    'high_school_gpa': ['Scatterplot'],
    'grade': ['Stacked Bar Graph'],
    'avg_dwf_rate': ['Bar Graph'],
    'race_ethnicity': ['Stacked Bar Graph'],
    'gender': ['Stacked Bar Graph'],
    'math_placement_score': ['Scatterplot'],
    'sat_total': ['Scatterplot'],
    'sat_math': ['Scatterplot'],
    'act_score': ['Scatterplot']
}

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
        var buttonStr = `<button class="h-25 col-2 btn btn-danger" onclick='removeCourseDropdownRow("row-${currentDropdownID}")'>X</button>`;
    } else {
        var buttonStr = '';
    }
    // Build the row, adding every course code.
    var row = `
        <div class="row align-items-center align-middle mb-4" id="row-${currentDropdownID}">
            <div class="col-4">
                <h6><strong>Select course...</strong></h6>
                <select class="form-select" id="course-${currentDropdownID}" onchange="addCorrespondingCourseSemesters(this, 'semester-${currentDropdownID}'); checkDropdowns();">
                    <option selected disabled>Choose a course...</option>
                    ${options}
                </select>
            </div> 
            <div class='col-5' style="margin-left: 10px;">
                <h6><strong>Select semester...</strong></h6>
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

/**
 * Fills the chartOrGraphTypeSelect with the correct chart or graph types for 
 * the selected column.
 */
function fillValidGraphTypes() {
    var columnSelect = document.getElementById('columnSelect');
    var selectedColumn = columnSelect.options[columnSelect.selectedIndex].value;
    var validChartGraphTypes = columnChartGraphMap[selectedColumn];

    var optionsString = '<option selected disabled value="Select a Chart/Graph Type">Select a Chart/Graph Type</option>\n';

    for (var chartGraphType of validChartGraphTypes) {
        optionsString += `<option value="${chartGraphType}">${chartGraphType}</option>\n`;
    }
    
    document.getElementById('chartOrGraphTypeSelect').innerHTML = optionsString;
}

function checkDropdowns() {
    function hasValidSelection(selectElement) {
        return selectElement.selectedIndex != 0;
    }

    var validDropdowns = true;

    // Check the dropdown for the chart/graph type.
    validDropdowns = validDropdowns && hasValidSelection(document
        .getElementById('chartOrGraphTypeSelect'));

    // Check to make sure a column in the dataset was selected.
    validDropdowns = validDropdowns && hasValidSelection(document
        .getElementById('columnSelect'));

    for (var i = 1; i <= currentDropdownID; i++) {
        var courseSelect = document.getElementById(`course-${i}`);
        var semesterSelect = document.getElementById(`semester-${i}`);

        if (courseSelect != null && semesterSelect != null) {
            validDropdowns = validDropdowns && (hasValidSelection(courseSelect) 
                && hasValidSelection(semesterSelect));
        }
    }

    if (validDropdowns) {
        document.getElementById('showChartGraphButton').disabled = false;
    } else {
        document.getElementById('showChartGraphButton').disabled = true;
    }
}

function downloadDivAsPDF(div, fileName) {
    html2canvas(div, {
        scale: 1
    }).then((canvas) => {
        var imgData = canvas.toDataURL('image/png');
        var doc = new jsPDF('l', 'in', [11, 5]);
        doc.addImage(imgData, 'PNG', 0, 0);
        doc.save(fileName);
    });
}

function buildChartOrGraph(chartGraphType, data, yAxisLabel) {
    const chartOrGraphDiv = document.createElement('div');
    const layout = {
        title: {
            text: `${yAxisLabel} per Course`
        },
        xaxis: {
            title: 'Course Number'
        },
        yaxis: {
            title: yAxisLabel
        },
        autosize: false,
        width: 950,
        height: 450,
        margin: {
            l: 50,
            r: 50,
            b: 100,
            t: 100,
            pad: 4
        }
    }

    const genBarGraph = () => {
        if (layout.barmode) {
            delete layout['barmode'];
        }

        var barList = [];
        
        for (var course in data) {
            // Check to see if the data is a single value or list.
            var yData = (typeof data[course] === Array ) ? data[course] : 
                [data[course]];
            barList.push({
                x: course,
                y: yData,
                name: course,
                type: 'bar'
            });
        }

        Plotly.newPlot(chartOrGraphDiv, barList, layout);
    };

    const genScatterplot = () => {
        var traceList = [];
        
    };

    const genStackedBarGraph = () => {
        layout.barmode = 'stack';

        // Check to see if the course grade is being looked at, race/ethnicity,
        // or gender.
        if (yAxisLabel == 'Course Grade') {
            
        } else if (yAxisLabel == 'Race/Ethnicity') {

        } else {
            
        }
    }

    switch (chartGraphType) {
        case 'Bar Graph':
            genBarGraph();
            break;
        case 'Scatterplot':
            genScatterplot();
            break;
        case 'Stacked Bar Graph':
            genStackedBarGraph();
            break;
    }

    return chartOrGraphDiv;
}

function showChartOrGraphPopUp(div) {
    alertify.alert('Generated Visual', div).set('resizable', true)
        .resizeTo(1000, 700);
}

function genChartOrGraph() {
    function getSelectedValue(selectElement) {
        return selectElement.options[selectElement.selectedIndex].value;
    }

    function getSelectedLabel(selectElement) {
        return selectElement.options[selectElement.selectedIndex].text;
    }

    var selectedData = {};

    // Get the column the user selected.
    var columnSelect = document.getElementById('columnSelect');
    selectedData.column = getSelectedValue(columnSelect);
    const yAxisLabel = getSelectedLabel(columnSelect);

    // Get the graph/chart type the user selected.
    const chartGraphType = getSelectedValue(document
        .getElementById('chartOrGraphTypeSelect'));
    
    selectedCourses = {};
    for (var i = 1; i <= currentDropdownID; i++) {
        var selectedCourse = getSelectedValue(document
                .getElementById(`course-${i}`));
        var selectedSemester = getSelectedValue(document
                .getElementById(`semester-${i}`));
        
        if (selectedCourse != null && selectedSemester != null){
            selectedCourses[selectedCourse] = selectedSemester;
        }
    }
    selectedData.selectedCourses = selectedCourses;

    fetch('/class-by-class-comparisons', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            accept: 'application/json'
        },
        body: JSON.stringify(selectedData)
    }).then((res) => res.json()).then((json) => {
        var div = buildChartOrGraph(chartGraphType, json, yAxisLabel);
        showChartOrGraphPopUp(div);
    });
}