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

function sendReset(evt) {
    evt.preventDefault();

    const password1 = document.getElementById('newPassword1').value;
    const password2 = document.getElementById('newPassword2').value;
    const statusP = document.getElementById('passwordStatusP');

    if (password1 != password2) {
        statusP.style.visibility = 'visible';
    } else {
        fetch('/reset', {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            method: 'POST',
            body: JSON.stringify({
                token: new URLSearchParams(window.location.search).get('token'),
                password: btoa(password1)
            })
        }).then((res) => {
            if (res.redirected) {
                window.location.href = res.url;
            }

            if (res.status == 400) {
                statusP.innerText = 'You cannot reset the password of a Google account.';
                statusP.style.visibility = 'visible';
            } else if (res.status == 409) {
                statusP.innerText = 'You can\'t reuse a previously used password.';
                statusP.style.visibility = 'visible';
            }
        });
    }
}

function checkPasswordFields() {
    const password1 = document.getElementById('newPassword1').value;
    const password2 = document.getElementById('newPassword2').value;
    const statusP = document.getElementById('passwordStatusP');
    const resetButton = document.getElementById('resetButton');

    if (statusP.style.visibility == 'visible') {
        statusP.style.visibility = 'hidden';
    }

    if (password1.trim() != '' && password2.trim() != '') {
        resetButton.disabled = false;
        resetButton.style.opacity = 100;
        resetButton.style.cursor = 'pointer';
    } else {
        resetButton.disabled = true;
        resetButton.style.opacity = 30;
        resetButton.style.cursor = 'not-allowed';
    }
}

function sendResetEmail(evt) {
    evt.preventDefault();

    const email = document.getElementById('emailField').value;
    const statusP = document.getElementById('emailStatusP');

    fetch('/sendreset', {
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            email: email
        })
    }).then((res) => {
        if (res.status == 200) {
            statusP.classList.remove('text-danger');
            statusP.classList.add('text-success');
            statusP.innerText = 'Email Sent. Please make sure to check your spam folder.';
            statusP.style.visibility = 'visible';
        } else if (res.status == 400) {
            statusP.classList.remove('text-success');
            statusP.classList.add('text-danger');
            statusP.value = 'That email is not associated with an account!';
            statusP.style.visibility = 'visible';
        }
    });
}

function checkEmailField() {
    const email = document.getElementById('emailField').value;
    const emailStatusP = document.getElementById('emailStatusP');
    const btn = document.getElementById('sendResetButton');

    if (emailStatusP.style.visibility == 'visible') {
        emailStatusP.style.visibility = 'hidden';
    }

    if (email !== '') {
        btn.disabled = false;
        btn.style.opacity = 100;
        btn.style.cursor = 'pointer';
    } else {
        btn.disabled = true;
        btn.style.opacity = 30;
        btn.style.cursor = 'not-allowed';
    }
}