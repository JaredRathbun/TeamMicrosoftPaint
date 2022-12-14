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
function changeUserRole(element, emailAddress) {
    var currentRole = element.dataset.default;
    var selectedRole = element.options[element.selectedIndex].text;
    var name = element.dataset.name;

    const getIndex = (role) => {
        switch (role) {
            case 'Admin':
                return 0;
            case 'Data Admin':
                return 1;
            case 'Viewer':
                return 2;
        }
    }
    // Pop up a confirmation for the user. 
    $.confirm({
        title: 'Confirm Role Change',
        content: `Are you sure you want to change ${name} from ${currentRole} to ${selectedRole}?`,
        buttons: {
            confirm: {
                btnClass: 'btn-primary',
                keys: ['enter'],
                action: () => {
                    fetch('/change-role', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            email: emailAddress,
                            new_role: selectedRole
                        })
                    }).then((res) => {
                        if (res.status == 200) {
                            $.alert({
                                title: 'Success!',
                                content: 'User role changed successfully!',
                                type: 'green',
                                typeAnimated: true
                            });
                        }
                    });
                }
            },
            cancel: {
                btnClass: 'btn-danger',
                keys: ['escape'],
                action: () => {
                    // Move back to the original index.
                    var defaultIdx = getIndex(currentRole);
                    element.selectedIndex = defaultIdx;
                }
            } 
        }
    })
}

function logout(evt) {
    evt.preventDefault();
    fetch('/logout', {method: 'POST'}).then((res) => {
        if (res.redirected) {
            window.location.href = res.url;
        }
    });
}

usersList = null, sortedUsersList = null;
window.onload = () => {
    fetch('/get-all-users').then((res) => res.json()).then((data) => {
        usersList = data;
        sortedUsersList = usersList.sort((val1, val2) => val1['name']
            .localeCompare(val2['name']));
        createUsersTable(usersList);
    })
}

function createUsersTable(data) {
    document.getElementById('usersTable').innerHTML = '';

    var bodyStr = '';
    for (var user of data) {
        var userStr = `
            <tr>
                <td>${user.name}</td>
                <td>${user.email}</td>
                <td>
                    <select onchange='changeUserRole(this, "${user.email}")'
                        class="form-select w-50" data-default=${user.role}
                        data-name=${user.name}>
        `;

        switch (user.role) {
            case 'Admin':
                userStr += `
                    <option selected value="1">Admin</option>
                    <option value="2">Data Admin</option>
                    <option value="3">Viewer</option>
                `;
                break;
            case 'Data Admin':
                userStr += `
                    <option value="1">Admin</option>
                    <option selected value="2">Data Admin</option>
                    <option value="3">Viewer</option>
                `;
                break;
            default:
                userStr += `
                    <option value="1">Admin</option>
                    <option value="2">Data Admin</option>
                    <option selected value="3">Viewer</option>
                `;
                break;
        }
        
        userStr += '</select></td></tr>';
        bodyStr += userStr;
    }

    var tableStr = `
        <thead>
            <tr>
                <th>User's Name</th>
                <th>Email Address</th>
                <th>Current Role</th>
            </tr>
        </thead>
        <tbody>
            ${bodyStr}
        </tbody>
    `;

    document.getElementById('usersTable').innerHTML = tableStr;
}

function searchForUser(element) {
    const searchVal = element.value;

    if (searchVal != '') {
        var start, end;
        for (var i = 0; i < sortedUsersList.length; i++) {
            if (sortedUsersList[i].name == searchVal) {
                if (start == undefined) {
                    start = i;
                } else {
                    end = i;
                }
            }
        }

        var copyList = sortedUsersList.splice(start, end + 1);
        createUsersTable(copyList);
    } else {
        createUsersTable(usersList);
    }
}