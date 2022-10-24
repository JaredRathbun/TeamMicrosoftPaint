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

let fileUpload = document.getElementById('fileUpload');
let uploadButton = document.getElementById('uploadButton');
fileUpload.addEventListener('change', () => {
    if (fileUpload.files.length == 0) {
        uploadButton.disabled = true;
    } else {
        uploadButton.disabled = false;
    }
});


uploadButton.addEventListener('click', async () => {
    // let file = fileUpload.files[0];
    // const data = new FormData();
    // data.append('file', file);
    // const req = new XMLHttpRequest();
    // req.onreadystatechange = () => {
    //     if (req.status == 200) {
    //         
    //     } else {
    //         console.log(req.responseText);
    //     }
    // };
    // req.open('POST', '/upload');
    // req.send(data);
    let file = fileUpload.files[0];
    const data = new FormData();
    data.append('file', file);
    const response = await fetch('/upload', {
        method: 'POST',
        body: data
    });

    if (response.status == 200) {
        $.alert({
                title: 'Success!',
                content: 'Data uploaded successfully!',
                type: 'green',
                typeAnimated: true
            });
    } else {
        const json = await response.json();
        $.dialog({
            title: 'Data Upload Failed',
            width: 500,
            type: 'red',
            content: buildTable(json)
        });
    }
});

function buildTable(data) {
    let error_str = '';
    for (const error of data.errors) { 
        error_str += `
            <tr>
                <td>${error.error_message}</td>
                <td>${error.line_num}</td>
                <td>${error.col_num}</td>
            </tr>
        `;
    }

    let return_str = `
    <div style='overflow-y: auto'>
        <h6>The following errors were found while uploading your data. Please consult the sample data for a guide as to how data should look.</h6>
        <table class='table table-responsive'>
            <thead>
                <tr>
                    <th>Error</th>
                    <th>Line Number</th>
                    <th>Column Number</th>
                </tr>
            </thead>
            <tbody>
                ${error_str}
            </tbody>
        </table>
    </div>
    `
    return return_str;
}