package com.teammspaint.stemdatadashboard.service;

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
import java.util.Base64;

import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;

import org.apache.commons.codec.binary.Base32;
import org.bouncycastle.jcajce.spec.ScryptKeySpec;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.teammspaint.stemdatadashboard.dao.User;
import com.teammspaint.stemdatadashboard.repository.UserRepository;

import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.Key;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.KeyStore;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.NoSuchProviderException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.SecureRandom;
import java.security.Security;
import java.security.Signature;
import java.security.SignatureException;
import java.security.UnrecoverableEntryException;
import java.security.cert.CertificateException;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.X509EncodedKeySpec;

/**
 * A Service for handling user authentication operations.
 */
@Service
public class UserService {

    @Autowired
    private UserRepository userRepo;

    /**
     * Verifies a user's password based on the password that is stored.
     * 
     * @param email The user's email address.
     * @param password The password the user entered.
     * 
     * @return A boolean representing if the password was correct or not.
     */
    public boolean verifyPassword(String email, String password) {
        Objects.requireNonNull(email, "Email address must not be null.");
        Objects.requireNonNull(password, "Password must not be null.");

        User usr = userRepo.findByEmail(email);
        
        return (usr == null) ? false : usr.verifyHash(password);
    }

    public boolean enrollUser(String email, String password, String firstName, 
        String lastName) {

        // Parameter checking.
        Objects.requireNonNull(email, "Email address must not be null.");
        Objects.requireNonNull(password, "Password must not be null.");
        Objects.requireNonNull(firstName, "First name must not be null.");
        Objects.requireNonNull(lastName, "Last name must not be null.");

        // Check to see if the user already exists.
        if (userRepo.findByEmail(email) != null) {
            return false;
        } else {
            User newUser = new User(firstName, lastName, email, password);
            userRepo.save(newUser);
            return true;
        }
    }

    /**
     * Returns whether or not the user is an admin.
     */
    public boolean isAdmin(String email) {
        Objects.requireNonNull(email);

        return userRepo.isAdmin(email);
    }
}
