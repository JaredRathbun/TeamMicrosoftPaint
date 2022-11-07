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

function logout(evt) {
    evt.preventDefault();
    fetch('/logout', { method: 'POST' }).then((res) => {
        if (res.redirected) {
            window.location.href = res.url;
        }
    });
}

var lowestEnabled = false;
function flipHighestLowestTable() {
    var highestBtn = document.getElementById('highest-btn');
    var lowestBtn = document.getElementById('lowest-btn');

    if (lowestEnabled) {
        lowestEnabled = false;
        highestBtn.disabled = true;
        lowestBtn.disabled = false;
        highestBtn.classList.add('btn-secondary');
        highestBtn.classList.remove('btn-primary');
        lowestBtn.classList.remove('btn-secondary');
        lowestBtn.classList.add('btn-primary');

        fetch('/average-dwf-rates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ part: 'highest' })
        })
            .then((res) => res.json())
            .then((data) => buildAVGDWFTable(data));
    } else {
        lowestEnabled = true;
        highestBtn.disabled = false;
        lowestBtn.disabled = true;
        highestBtn.classList.remove('btn-secondary');
        highestBtn.classList.add('btn-primary');
        lowestBtn.classList.add('btn-secondary');
        lowestBtn.classList.remove('btn-primary');

        fetch('/average-dwf-rates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ part: 'lowest' })
        })
            .then((res) => res.json())
            .then((data) => buildAVGDWFTable(data));
    }
}

function buildAVGDWFTable(data) {
    var bodyString = '';

    // Build the table.
    for (const course of data) {
        var row = `
            <tr class='d-flex'>
                <td class='col-3'>${course.course_num}</td>
                <td class='col-3'>${course.semester}</td>
                <td class='col-3'>${course.year}</td>
                <td class='col-3'>${course.avg_dwf}%</td>
            </tr>
        `
        bodyString += row;
    }

    // Set the body of the table.
    document.getElementById('dwf-rates-table-body').innerHTML = bodyString;
}

window.onload = () => {
    // Get the highest DWF rates.
    fetch('/average-dwf-rates', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ part: 'highest' })
    })
        .then((res) => res.json())
        .then((data) => buildAVGDWFTable(data));

    fetch('/avg-gpa-and-dwf-per-semester')
        .then((res) => res.json())
        .then((data) => buildAvgGpaAndDwfPerSemesterChart(data));

    fetch('/avg-gpa-per-cohort')
        .then((res) => res.json())
        .then((data) => buildAvgGpaPerCohortChart(data));
}

function buildAvgGpaPerCohortChart(data) {
    var cohorts = [], gpas = [];

    cohorts.push('Freshman');
    gpas.push(data['Freshman']);

    cohorts.push('Sophomore');
    gpas.push(data['Sophomore']);

    cohorts.push('Junior');
    gpas.push(data['Junior']);

    cohorts.push('Senior');
    gpas.push(data['Senior']);

    var data = [
        {
            x: cohorts,
            y: gpas,
            type: 'bar',
            marker: {
                color: 'rgb(0, 123, 255)'
            }
        }
    ];

    var layout = {
        margin: {
            l: 45,
            r: 45,
            b: 45,
            t: 45
        },
        xaxis: {
            title: {
              text: 'Class Cohort'
            },
          },
        yaxis: {
            autorange: false,
            range: [0.0, 4.0],
            title: {
                text: 'GPA'
            }
        },
    };

    Plotly.newPlot('avg-gpa-per-cohort-div', data, layout, {responsive: true});
}

function downloadAvgStudentGPADWFRateAsPDF() {
    var div = document.getElementById('avg-gpa-and-course-dwf-per-semester');

    html2canvas(div, {
        scale: 1
    }).then((canvas) => {
        var imgData = canvas.toDataURL('image/png');
        var doc = new jsPDF('l', 'in', [11, 5]);
        doc.addImage(imgData, 'PNG', 0, 0);
        doc.save('average_gpa_an_dwf_per_semester.pdf');
    });
}

function downloadAvgGPAPerCohortAsPDF() {
    var div = document.getElementById('avg-gpa-per-cohort-div');

    html2canvas(div, {
        scale: 1
    }).then((canvas) => {
        var imgData = canvas.toDataURL('image/png');
        var doc = new jsPDF('p', 'in', [5, 5]);
        doc.addImage(imgData, 'PNG', 0, 0);
        doc.save('average_gpa_per_cohort.pdf');
    });
}

function buildAvgGpaAndDwfPerSemesterChart(json) {
    var semesters = [], gpas = [], dwfs = [];
    for (var semester in json) {
        semesters.push(semester);
        gpas.push(json[semester]['avg_gpa']);
        dwfs.push(json[semester]['avg_dwf'])
    }

    var data = [
        {
            x: semesters,
            y: gpas,
            name: 'Average GPA',
            type: 'bar',
            marker: {
                color: 'rgb(0, 123, 255)'
            }
        },
        {
            x: semesters,
            y: dwfs,
            name: 'DWF Rate',
            type: 'bar',
            marker: {
                color: 'rgb(40, 167, 69)'
            }
        }
    ];

    var layout = {
        margin: {
            l: 30,
            r: 30,
            b: 30,
            t: 30
        }
    };

    Plotly.newPlot('avg-gpa-and-course-dwf-per-semester', data, layout, {responsive: true});
}


// This page is super helpful: https://stackoverflow.com/questions/6887183/how-to-take-screenshot-of-a-div-with-javascript
function downloadNumOfStudentsPerMajorAsPNG(e) {
    e.preventDefault();

    const div = document.getElementById('num-students-per-major-div');

    window.scrollTo(0, 0);
    html2canvas(div, {
        scale: 1
    }).then((canvas) => {
        canvas.toBlob(function (blob) {
            saveAs(blob, "num_of_students_per_course.png");
        });
    });
}

function downloadNumOfStudentsPerMajorAsJPG(e) {
    e.preventDefault();

    const div = document.getElementById('num-students-per-major-div');

    window.scrollTo(0, 0);
    html2canvas(div).then((canvas) => {
        canvas.toBlob(function (blob) {

            saveAs(blob, "num_of_students_per_course.jpg");
        });
    });
}