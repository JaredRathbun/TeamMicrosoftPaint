package com.teammspaint.stemdatadashboard.dao;

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
import javax.persistence.Column;

import com.teammspaint.stemdatadashboard.auth.oauth.Provider;

import java.util.Objects;
import java.util.Base64;

import javax.crypto.KeyGenerator;
import javax.crypto.Mac;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.SecretKeySpec;

import org.apache.commons.codec.binary.Base32;
import org.bouncycastle.jcajce.spec.ScryptKeySpec;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.threeten.bp.Instant;

import com.teammspaint.stemdatadashboard.dao.User;

import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.Security;
import java.security.spec.InvalidKeySpecException;

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

    @Column(name = "TOTP_KEY")
    private String TOTP_KEY;

    /**
     * Logger instance.
     */
    private static final Logger logger = LoggerFactory.getLogger(User.class); 

    public User() {}

    /**
     * Creates a new user that is provided locally. (NOTE THE PASSWORD PARAM)
     * 
     * @param firstName    The user's first name.
     * @param lastName     The user's last name.
     * @param emailAddress The user's email address.
     * @param password     The user's password.
     */
    public User(String firstName, String lastName, String emailAddress,
            String password) {

        // Parameter checking.
        Objects.requireNonNull(emailAddress, "Email address must not be null.");
        Objects.requireNonNull(password, "Password must not be null.");
        Objects.requireNonNull(firstName, "First name must not be null.");
        Objects.requireNonNull(lastName, "Last name must not be null.");

        this.firstName = firstName;
        this.lastName = lastName;
        this.emailAddress = emailAddress;
        this.provider = Provider.LOCAL;
        
        try {
            // Generate the TOTP Key.
            this.TOTP_KEY = genTOTPKey();
        } catch (NoSuchAlgorithmException ex) {
            logger.error("Unable to generate TOTP Key for user {}", 
                this.emailAddress);
        }

        // Generate a new salt, then hash the password.
        byte[] salt = generateSalt();
        this.salt = Base64.getEncoder().encodeToString(salt);
        this.hash = Base64.getEncoder().encodeToString(hash(password, salt));
    }

    /**
     * Creates a new user that is provided by Google.
     * 
     * @param firstName    The user's first name.
     * @param lastName     The user's last name.
     * @param emailAddress The user's email address.
     */
    public User(String firstName, String lastName, String emailAddress) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.emailAddress = emailAddress;
        this.provider = Provider.GOOGLE;

        try {
            // Generate the TOTP Key.
            this.TOTP_KEY = genTOTPKey();
        } catch (NoSuchAlgorithmException ex) {
            logger.error("Unable to generate TOTP Key for user {}", 
                this.emailAddress);
        }
    }

    @Override
    public String toString() {
        return String.format("User[%d %s, %s, %s, %s]", id, lastName, firstName,
                emailAddress, provider);
    }

    public boolean verifyHash(String password) {
        byte[] salt = Base64.getDecoder().decode(this.salt);
        String genHash = Base64.getEncoder()
            .encodeToString(hash(password, salt));
        
        return genHash.equals(this.hash);
    }

    /**
     * This method gets the TOTPKey in a Base32 String format.
     *
     * @return A String representing the TOTP Key.
     * @throws NoSuchAlgorithmException If "HmacSHA1" is an invalid algorithm.
     */
    private String genTOTPKey() throws NoSuchAlgorithmException {
        byte[] keyMaterial = KeyGenerator.getInstance("HmacSHA1")
                .generateKey().getEncoded();

        return new Base32().encodeAsString(keyMaterial);
    }

    /**
     * This method hashes a salt and password together using SCRYPT.
     *
     * @param password The password the user entered.
     * @param salt The salt to hash with the password.
     * @return A byte representation of the hashed password and salt.
     */
    private byte[] hash(String password, byte[] salt) {
        // Add the Bouncy Castle Provider.
        Security.addProvider(new BouncyCastleProvider());

        // The ScriptKeySpec object.
        ScryptKeySpec scryptSpec = new ScryptKeySpec(password.toCharArray(), 
            salt, 2048, 8, 1, 128);

        SecretKey key = null;

        try {
            // Create the new SecretKey object.
            key = SecretKeyFactory.getInstance("SCRYPT")
                    .generateSecret(scryptSpec);
        } catch (NoSuchAlgorithmException | InvalidKeySpecException e) {
            System.err.println("Error creating Secret Key from password."
                    + e.getMessage());
            e.printStackTrace();
        }

        return key.getEncoded();
    }

    /**
     * This method generates a salt or IV uniformly at random using Java's
     * SecureRandom object.
     *
     * @return A random 16-bit byte array.
     */
    private byte[] generateSalt() {
        SecureRandom rand = new SecureRandom();
        byte[] salt = new byte[16];
        rand.nextBytes(salt);

        return salt;
    }

    public int getOTP() {
        byte[] hmacKey = new Base32().decode(this.TOTP_KEY);

        long state = (long) Math.floor(Instant.now().getEpochSecond() / 30);

        return hotp(hmacKey, longToBytes(state));
    }

    /**
     * This method calculates a one time password by using HOTP.
     *
     * @param hmacKey The HMAC-SHA1 key.
     * @param sinceEpoch The time since the Unix Epoch (January 1, 1970 @ 12AM).
     * @return An integer representing the OTP.
     */
    private int hotp(byte[] sinceEpoch, byte[] hmacKey)
    {
        // A key for signing.
        SecretKeySpec signKey = new SecretKeySpec(hmacKey, "HmacSHA1");

        // Sign the byte array.
        byte[] hash = null;

        try
        {
            Mac mac = Mac.getInstance("HmacSHA1");
            mac.init(signKey);
            hash = mac.doFinal(sinceEpoch);
        } catch (NoSuchAlgorithmException | InvalidKeyException e)
        {
            logger.error("Unable to generate HOTP code for user.");
        }

        // Pack the hash into a 4-bit integer.
        int shiftIdx = hash[19] & 0xF;

        // Pack the bytes into an integer.
        int result;

        result = (hash[shiftIdx] & 0x7F) << 24;
        result = result | ((hash[shiftIdx + 1] & 0xff) << 16);
        result = result | ((hash[shiftIdx + 2] & 0xff) << 8);
        result = result | (hash[shiftIdx + 3] & 0xff);

        return (result % 1000000);
    }

    /**
     * This method converts a long value into an 8-byte value.
     *
     * @author Zach Kissel - Our Lord and Savior
     * @param num the number to convert to bytes.
     * @return an array of 8 bytes representing the number num.
     */
    private byte[] longToBytes(long num)
    {
        byte[] res = new byte[8];

        // Decompose the a long type into byte components .
        for (int i = 7; i >= 0; i--)
        {
            res[i] = (byte) (num & 0xFF);
            num >>= 8;
        }

        return res;
    }
}
