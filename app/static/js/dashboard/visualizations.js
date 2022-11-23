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

/**
 * Dynamically sets the semesters that match the course that was selected in the
 * courseSelect HTML Element.
 * 
 * @param {HTMLElement} courseSelect The select HTML element.
 * @param {*} selectID The ID of the select element that holds the semesters for 
 * the corresponding course.
 */
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
    document.getElementById('classByClassGenerateButton').disabled = true;
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

/**
 * Checks to make sure all dropdowns have a valid selection and enables the 
 * "Generate Graph/Chart" button if they are.
 */
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
        document.getElementById('classByClassGenerateButton').disabled = false;
    } else {
        document.getElementById('classByClassGenerateButton').disabled = true;
    }
}

/**
 * Converts the given div element to a PDF and downloads it under the given 
 * filename on the user's browser.
 * 
 * @param {HTMLElement} div The div to convert to a PDF.
 * @param {String} fileName The filename to save the PDF as.
 */
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

/**
 * Builds the correct chart/graph for the selected graph type with the specified
 * data.
 * 
 * @param {String} chartGraphType A string representing what type of chart/graph
 * should be generated.
 * @param {Object} data The data to fill the chart/graph with.
 * @param {String} yAxisLabel A string representing the label for the Y-axis.
 * @returns A div that is styled with the chart/graph.
 * 
 * NOTE: Yes, there are too many closures in this function. :)
 */
function buildChartOrGraph(chartGraphType, data, yAxisLabel) {
    const chartOrGraphDiv = document.createElement('div');
    const layout = {
        autosize: false,
        width: 920,
        height: 450,
        margin: {
            l: 50,
            r: 50,
            b: 100,
            t: 100,
            pad: 4
        }
    }

    /**
     * Generates a Bar Graph.
     */
    const genBarGraph = () => {
        layout.title = {
            text: `${yAxisLabel} per Course`
        };
        layout.xaxis = {
            title: 'Course Number'
        };
        layout.yaxis = {
            title: yAxisLabel
        };

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

    /**
     * Generates a scatterplot.
     */
    const genScatterplot = () => {
        layout.title = {
            text: `${yAxisLabel} per Course`
        };
        layout.xaxis = {
            showline: true,
            showticklabels: false,
            title: 'Courses'
        };
        layout.yaxis = {
            title: yAxisLabel
        }

        var courseTraceList = [];

        for (var course in data) {
            courseTraceList.push({
                x: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                y: data[course],
                mode: 'markers',
                type: 'scatter',
                name: course
            });
        }
        
        Plotly.newPlot(chartOrGraphDiv, courseTraceList, layout);
    };

    /**
     * Generates a Stacked Bar Graph.
     */
    const genStackedBarGraph = () => {
        layout.barmode = 'stack';
        layout.title = {
            text: `${yAxisLabel} per Course`
        };
        layout.xaxis = {
            title: yAxisLabel
        };
        layout.yaxis = {
            title: 'Number of Students'
        };
        var barList = [];

        // Check to see if the course grade is being looked at, race/ethnicity,
        // or gender.
        if (yAxisLabel == 'Course Grade') {
            for (var course in data) {
                gradeObj = {
                    'A': 0, 'A-': 0, 'B+': 0, 'B': 0, 'B-': 0, 'C+': 0, 'C': 0,
                    'C-': 0, 'D+': 0, 'D': 0, 'D-': 0, 'W': 0, 'F': 0, 'P': 0, 
                    'W': 0
                };

                for (var grade of data[course]) {
                    console.log(grade);
                    gradeObj[grade] = gradeObj[grade] + 1;
                }

                var gradeList = [], gradeCountList = [];
                Object.keys(gradeObj).forEach((key) => {
                    gradeList.push(key);
                    gradeCountList.push(gradeObj[key]);
                });
                
                barList.push({
                    x: gradeList,
                    y: gradeCountList,
                    name: course,
                    type: 'bar'
                });
            }
        } else if (yAxisLabel == 'Race/Ethnicity') {
            for (var course in data) {
                var whiteCount = 0, hispCount = 0, blackCount = 0, 
                    asianCount = 0, americanIndianOrAlaskaNativeCount = 0, 
                    nativeHawaiianOrOtherCount = 0;

                for (var raceEthnicity of data[course]) {
                    switch (raceEthnicity) {
                        case 'WH':
                            whiteCount++;
                            break;
                        case 'HISP':
                            hispCount++;
                            break;
                        case 'BL':
                            blackCount++;
                            break;
                        case 'AS':
                            asianCount++;
                            break;
                        case 'NO':
                            nativeHawaiianOrOtherCount++;
                            break;
                        // Need to verify with Jimmy/Stuetzle and ask what the 
                        // proper abbreviations are.

                    }
                }

                barList.push({
                    x: ['White', 'Black/African American', 'Hispanic/Latino',
                         'Asian', 'American Indian/Alaska Native', 
                         'Native Hawaiian/Other'],
                    y: [whiteCount, blackCount, hispCount, asianCount, 
                        americanIndianOrAlaskaNativeCount, 
                        nativeHawaiianOrOtherCount],
                    name: course,
                    type: 'bar'
                });
            }
        } else {
            for (var course in data) {
                var maleCount = 0, femaleCount = 0;
                for (var gender of data[course]) {
                    if (gender == 'M') {
                        maleCount++;
                    } else {
                        femaleCount++;
                    }
                }

                barList.push({
                    x: ['Female', 'Male'],
                    y: [femaleCount, maleCount],
                    name: course,
                    type: 'bar'
                });
            }
        }

        Plotly.newPlot(chartOrGraphDiv, barList, layout);
    }

    // Generates the correct chart/graph based on what the user selected.
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

/**
 * Generates a pop up that is filled with the specified div, which should have
 * a chart/graph in it.
 * 
 * @param {HTMLElement} div The div element to show in the pop up.
 */
function showChartOrGraphPopUp(div) {
    alertify.alert('Generated Visual', div).set('resizable', true)
        .resizeTo(1000, 600);
}

/**
 * Gets the selected options from the user, then calls the appropriate function
 * to generate a chart/graph.
 */
function genClassByClassChartOrGraph() {
    /**
     * Returns the value of the selected option element inside of the specified 
     * select element.
     * @param {HTMLElement} selectElement The HTML Select element.
     * @returns A string containing the value of the selected option element.
     */
    function getSelectedValue(selectElement) {
        return selectElement.options[selectElement.selectedIndex].value;
    }

    /**
     * Gets the label/text that is inside of the selected option in the given
     * select element.
     * 
     * @param {HTMLSelectElement} selectElement The Select Element to get the 
     * label of.
     * 
     * @returns A string containing the label of the selected option. 
     */
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
    
    // Walk over every course dropdown, and get the course and semester.
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
    // Make the request to the backend to get the data.
    fetch('/class-by-class-comparisons', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            accept: 'application/json'
        },
        body: JSON.stringify(selectedData)
    }).then((res) => res.json()).then((json) => {
        // Build the div containing the appropriate chart/graph, then show it.
        var div = buildChartOrGraph(chartGraphType, json, yAxisLabel);
        showChartOrGraphPopUp(div);
    });
}

function fillValidHighestYears(lowestSelectElement, highestYear){

     /**
     * Returns the value of the selected option element inside of the specified 
     * select element.
     * @param {HTMLElement} selectElement The HTML Select element.
     * @returns A string containing the value of the selected option element.
     */
      function getSelectedValue(selectElement) {
        return selectElement.options[selectElement.selectedIndex].value;
    }

    var lowestSelectedValue = getSelectedValue(lowestSelectElement);
    var highestSelect = document.getElementById('highestYearSelect');

    var optionsString = '<option selected disabled value="Choose an End Year: ">Select an End Year </option>\n';

    for (var i = lowestSelectedValue; i <= highestYear; i++){
        optionsString += `<option value="${i}"> ${i}</option>\n`;
    }
    highestSelect.innerHTML = optionsString;
}


function genCovidGraph(){
     /**
     * Returns the value of the selected option element inside of the specified 
     * select element.
     * @param {HTMLElement} selectElement The HTML Select element.
     * @returns A string containing the value of the selected option element.
     */
      function getSelectedValue(selectElement) {
        return selectElement.options[selectElement.selectedIndex].value;
    }

    /**
     * Gets the label/text that is inside of the selected option in the given
     * select element.
     * 
     * @param {HTMLSelectElement} selectElement The Select Element to get the 
     * label of.
     * 
     * @returns A string containing the label of the selected option. 
     */
    function getSelectedLabel(selectElement) {
        return selectElement.options[selectElement.selectedIndex].text;
    }

    var selectedData = {};

    // Get the column the user selected.
    var columnSelect = document.getElementById('covidData');
    selectedData.column = getSelectedValue(columnSelect);
    const yAxisLabel = getSelectedLabel(columnSelect);
    
    // 
    var avgColumnData = Utils.get_covid_data('covidData');

    // Make the request to the backend to get the data.
    fetch('/covid-data-comparison', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            accept: 'application/json'
        },
        body: JSON.stringify(avgColumnData)
    }).then((res) => res.json()).then((json) => {
        // Build the div containing the appropriate chart/graph, then show it.
        var div = buildCovidChart(json, yAxisLabel);
        showChartOrGraphPopUp(div);
    });
}

function buildCovidChart(data, yAxisLabel) {
    const chartOrGraphDiv = document.createElement('div');
    const layout = {
        autosize: false,
        width: 920,
        height: 450,
        margin: {
            l: 50,
            r: 50,
            b: 100,
            t: 100,
            pad: 4
        }
    }

    genBarGraph();

    /**
     * Generates a Bar Graph.
     */
    const genBarGraph = () => {
        layout.title = {
            text: `${yAxisLabel} per Year`
        };
        layout.xaxis = {
            title: 'Covid Years'
        };
        layout.yaxis = {
            title: yAxisLabel
        };

        var xValue = ['SP 2020', 'FA 2020','SP 2021','FA 2021'];

        var yValue = data;

        var barList = {
             x: xValue,
             y: yValue,
            type: 'bar',
            text: yValue.map(String),
            textposition: 'auto',
            hoverinfo: 'none',
            marker: {
            color: 'rgb(158,202,225)',
            opacity: 0.6,
            line: {
            color: 'rgb(8,48,107)',
            width: 1.5
             }
         }
        };

        Plotly.newPlot(chartOrGraphDiv, barList, layout);
    };
}