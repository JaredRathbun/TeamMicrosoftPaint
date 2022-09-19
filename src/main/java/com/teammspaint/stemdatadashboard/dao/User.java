package com.teammspaint.stemdatadashboard.dao;

import javax.persistence.Column;

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

import javax.persistence.Entity;
import javax.persistence.EnumType;
import javax.persistence.Enumerated;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.Table;

import com.teammspaint.stemdatadashboard.oauth.Provider;

@Entity
@Table(name = "USERS")
public class User {
    @Id
    @Column(name = "ID")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "FIRST_NAME", nullable = false)
    private String firstName;
    
    @Column(name = "LAST_NAME", nullable = false)
    private String lastName;
    
    @Column(name = "EMAIL_ADDRESS", nullable = false)
    private String emailAddress;
    
    @Column(name = "HASH")
    private String hash;
    
    @Column(name = "SALT")
    private String salt;

    @Enumerated(EnumType.STRING)
    private Provider provider;

    @Column(name = "IS_ADMIN", nullable = false)
    private boolean isAdmin;

    public User() {}
    
    /**
     * Creates a new user that is provided locally. (NOTE THE PASSWORD PARAM)
     * 
     * @param firstName The user's first name.
     * @param lastName The user's last name.
     * @param emailAddress The user's email address.
     * @param hash The user's password.
     */
    public User(String firstName, String lastName, String emailAddress, 
            String password) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.emailAddress = emailAddress;
        this.provider = Provider.LOCAL;

        // Generate a new salt, then concatenate it with password and hash it.
    }

    /**
     * Creates a new user that is provided by Google.
     * 
     * @param firstName The user's first name.
     * @param lastName The user's last name.
     * @param emailAddress The user's email address.
     */
    public User(String firstName, String lastName, String emailAddress) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.emailAddress = emailAddress;
        this.provider = Provider.GOOGLE;
    }

    @Override
    public String toString() {
        return String.format("User[%d %s, %s, %s, %s]", id, lastName, firstName,
             emailAddress, provider);
    }
}
