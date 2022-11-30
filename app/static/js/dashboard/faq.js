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

const checkFields = () => {
    const name = document.getElementById('nameField').value;
    const email = document.getElementById('emailField').value;
    const subject = document.getElementById('subjectField').value;
    const message = document.getElementById('messageField').value;
    const submitButton = document.getElementById('submitButton');

    if (name.trim() != '' && email.trim() != '' && subject.trim() != '' && 
        message.trim() != '') {
        submitButton.disabled = false;
    } else {
        submitButton.disabled = true;
    }
}

const sendContactEmail = (evt) => {
    evt.preventDefault();

    const name = document.getElementById('nameField').value;
    const email = document.getElementById('emailField').value;
    const subject = document.getElementById('subjectField').value;
    const message = document.getElementById('messageField').value;

    fetch('/email-suggestion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            accept: 'application/json'
        },
        body: JSON.stringify({
            name: name,
            email: email,
            subject: subject,
            message: message
        })
    }).then((res) => {
        if (res.status == 200) {
            $.alert({
                title: 'Success!',
                content: 'Message sent!',
                type: 'green',
                typeAnimated: true
            });
        } else {
            $.dialog({
                title: 'Something went wrong!',
                content: 'Sorry, it looks like something didn\'t work right. Please try again later!',
                type: 'red',
                typeAnimated: true
            });
        }
    });
}