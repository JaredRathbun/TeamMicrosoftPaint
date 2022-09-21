package com.teammspaint.stemdatadashboard.auth;

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

import java.io.Serializable;
import java.util.Objects;

import javax.servlet.http.HttpSessionBindingEvent;
import javax.servlet.http.HttpSessionBindingListener;

import org.springframework.stereotype.Component;

/**
 * Referenced from: https://www.baeldung.com/spring-security-track-logged-in-users
 * 
 * @author Jared Rathbun
 * @version 1.0.0
 */
@Component
public class LoggedUser implements HttpSessionBindingListener, Serializable {

    private String email;
    private ActiveUserStore activeUserStore;

    public LoggedUser(String email, ActiveUserStore activeUserStore) {
        this.email = Objects.requireNonNull(email, "Email must not be null.");
        this.activeUserStore = Objects.requireNonNull(activeUserStore, 
            "ActiveUserStore must not be null.");
    }

    public LoggedUser() {}

    /**
     * Binds the user to the activeUserStore.
     */
    @Override
    public void valueBound(HttpSessionBindingEvent evt) {
        LoggedUser usr = (LoggedUser) evt.getValue();
        String email = usr.getEmail();
        // If the user is not in the store, add them.
        if (!activeUserStore.verifyUser(email)) {
            activeUserStore.storeUser(email);
        }
    }

    /**
     * Unbinds the user from the activeUserStore.
     */
    @Override
    public void valueUnbound(HttpSessionBindingEvent evt) {
        LoggedUser usr = (LoggedUser) evt.getValue();
        String email = usr.getEmail();

        // If the user is in the store, remove them.
        if (activeUserStore.verifyUser(email)) {
            activeUserStore.removeUser(email);
        }
    }

    /**
     * Returns the email associated with the user.
     * 
     * @return The user's email.
     */
    public String getEmail() {
        return this.email;
    }
}
