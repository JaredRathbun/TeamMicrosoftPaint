package com.teammspaint.stemdatadashboard.auth;

import java.util.ArrayList;

/**
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
*/

import java.util.Objects;

import org.springframework.stereotype.Component;

/**
 * A class to keep track of users that are currently logged in.
 */
@Component
public class ActiveUserStore {

    /**
     * A list of logged in users.
     */
    private ArrayList<String> users;

    public ActiveUserStore() {
        users = new ArrayList<>();
    }

    /**
     * Returns a new instance of the user store.
     * 
     * @return A new instance of the user store.
     */
    public ActiveUserStore activeUserStore() {
        return new ActiveUserStore();
    }

    /**
     * Stores a user as logged in.
     * 
     * @param email The email address of the user.
     */
    public void storeUser(final String email) {
        Objects.requireNonNull(email, "Email must not be null.");

        if (email.equals("")) {
            throw new IllegalArgumentException("Provided email was empty.");
        }

        users.add(email);
    }

    /**
     * Verifies if a user is stored or not.
     * 
     * @param email The user's email.
     * 
     * @return A boolean representing whether or not the UUID is valid.
     */
    public boolean verifyUser(final String email) {
        Objects.requireNonNull(email, "Email must not be null.");

        if (email.equals("")) {
            throw new IllegalArgumentException("Provided email was empty.");
        }

        return (users.contains(email));
    }

    /**
     * Removes the stored user from the user store.
     * 
     * @param email The email of the user.
     */
    public void removeUser(final String email) {
        Objects.requireNonNull(email, "Email must not be null.");

        if (email.equals("")) {
            throw new IllegalArgumentException("Provided email was empty.");
        } else {
            users.remove(email);
        }
    }
}
