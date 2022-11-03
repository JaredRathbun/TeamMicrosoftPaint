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
            body: JSON.stringify({part: 'highest'})
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
            body: JSON.stringify({part: 'lowest'})
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
        body: JSON.stringify({part: 'highest'})
    })
    .then((res) => res.json())
    .then((data) => buildAVGDWFTable(data));
}