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

function checkFields() {
    const first_name = document.getElementById('firstNameField').value;
    const last_name = document.getElementById('lastNameField').value;
    const email = document.getElementById('emailField').value;
    const password1 = document.getElementById('passwordField1').value;
    const password2 = document.getElementById('passwordField2').value;
    const statusP = document.getElementById('statusP');
    const registerBtn = document.getElementById('registerButton');

    if (statusP.style.visibility == 'visible') {
        statusP.style.visibility = 'hidden';
    } 

    if (first_name.trim() != "" && last_name.trim() != "" && email.trim() != "" 
        && password1.trim() != "" && password2.trim() != "") {
        registerBtn.disabled = false;
        registerBtn.style.opacity = 100;
        registerBtn.style.cursor = 'pointer';
    } else {
        registerBtn.disabled = true;
        registerBtn.style.opacity = 30;
        registerBtn.style.cursor = 'not-allowed';
    }
}

function sendRegister(evt) {
    evt.preventDefault();

    const first_name = document.getElementById('firstNameField').value;
    const last_name = document.getElementById('lastNameField').value;
    const email = document.getElementById('emailField').value;
    const password1 = document.getElementById('passwordField1').value;
    const password2 = document.getElementById('passwordField2').value;
    const statusP = document.getElementById('statusP');

    if (password1 != password2) {
        statusP.innerText = 'Your passwords do not match.';
        statusP.style.visibility = 'visible';
    } else {
        fetch('/register', {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            method: 'POST',
            body: JSON.stringify({
                first_name: first_name,
                last_name: last_name,
                email: email,
                password: btoa(password1)
            })
        }).then((res) => {
            if (res.redirected) {
                statusP.classList.remove('text-danger');
                statusP.classList.add('text-success');
                statusP.innerText = 'Your account has been created!';
                statusP.style.visibility = 'visible';

                // Create timer for 3 seconds before redirecting.
                setTimeout(() => {
                    window.location.href = res.url;
                }, 2500);
            }

            if (res.status == 409) {
                statusP.innerText = 'An account already exists with that email.';
                statusP.style.visibility = 'visible';
            } else if (res.status == 500) {
                statusP.innerText = 'It looks like we couldn\'t process that request.\nPlease try again!';
                statusP.style.visibility = 'visible';
            }
        });
    }
}