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

function sendOTP(evt) {
    evt.preventDefault();

    const email = window.location.pathname.split('/')[2];

    fetch('/otp/' + email, {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            otp: document.getElementById('otpField').value
        })
    }).then((res) => {
        if (res.redirected) {
            window.location.href = res.url;
        }
        
        if (res.status == 401) {
            document.getElementById('statusP').style.visibility = 'visible';
        }
    })
}

function checkEmailField() {
    const otp = document.getElementById('otpField').value;
    const statusP = document.getElementById('statusP');
    const btn = document.getElementById('otpButton');

    if (statusP.style.visibility == 'visible') {
        statusP.style.visibility = 'hidden';
    }

    if (otp !== '' || otp.length < 6) {
        btn.disabled = false;
        btn.style.opacity = 100;
        btn.style.cursor = 'pointer';
    } else {
        btn.disabled = true;
        btn.style.opacity = 30;
        btn.style.cursor = 'not-allowed';
    }
}