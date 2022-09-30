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

function sendLogin(e) {
    e.preventDefault();

    const email = document.getElementById("emailField").value;
    const password = document.getElementById('passwordField').value;
    const statusP = document.getElementById('status-p');

    statusP.style.visibility = 'hidden';

    // Send the login request.
    fetch('/login', {
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            email: email,
            password: btoa(password)
        })
    }).then((res) => {
        if (res.redirected) {
            window.location.href = res.url;
        }

        if (res.status == 406) {
            statusP.innerText = 'You cannot login with a merrimack.edu email.' + 
                ' Please use the Login with Google button!';
            statusP.style.visibility = 'visible';
        } else if (res.status == 401) {
            statusP.innerText = 'Invalid Email/Password';
            statusP.style.visibility = 'visible';
        }
    });
}

function checkFields() {
    const email = document.getElementById("emailField").value;
    const password = document.getElementById('passwordField').value;
    const loginButton = document.getElementById('login-button');
    const statusP = document.getElementById('status-p');

    if (statusP.style.visibility == 'visible') {
        statusP.style.visibility = 'hidden';
    }

    if (email.trim() != "" && password.trim() != "") {
        loginButton.disabled = false;
        loginButton.style.opacity = 100;
        loginButton.style.cursor = 'pointer';
    } else {
        loginButton.disabled = true;
        loginButton.style.opacity = 30;
        loginButton.style.cursor = 'not-allowed';
    }
}