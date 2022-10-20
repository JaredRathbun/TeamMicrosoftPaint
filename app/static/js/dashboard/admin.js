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

let fileUpload = document.getElementById('fileUpload');
let uploadButton = document.getElementById('uploadButton');
fileUpload.addEventListener('change', () => {
    if (fileUpload.files.length == 0) {
        uploadButton.disabled = true;
    } else {
        uploadButton.disabled = false;
    }
});


uploadButton.addEventListener('click', () => {
    let file = fileUpload.files[0];
    // fetch('/upload', {
    //     method: 'POST',
    //     headers: {
    //         'Content-Type': 'multipart/form-data'
    //     },
    //     body: file
    // }).then((res) => res.json())
    // .then((data) => {
    //     console.log(data);
    //     // if (res.status == 200) {
    //     //     alert('Success');
    //     // } else {
    //     //     console.log(res);
    //     // }
    // });
    const data = new FormData();
    data.append('file', file);
    const req = new XMLHttpRequest();
    req.onreadystatechange = () => {
        if (req.status == 200) {
            alert('good!');
        } else {
            console.log(req.responseText);
        }
    };
    req.open('POST', '/upload');
    req.send(data);
});

function changeUserPermissions(element, emailAddress) {
    console.log(element);
    console.log(emailAddress);
}

function logout(evt) {
    evt.preventDefault();
    fetch('/logout', {method: 'POST'}).then((res) => {
        if (res.redirected) {
            window.location.href = res.url;
        }
    });
}