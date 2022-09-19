package com.teammspaint.stemdatadashboard.oauth;

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

import java.util.Collection;
import java.util.Map;

import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.oauth2.core.user.OAuth2User;

/**
 * A DAO for OAuth2 User.
 * 
 * @author Jared Rathbun
 * 
 * Sourced from: https://www.codejava.net/frameworks/spring-boot/oauth2-login-with-google-example
 */
public class CustomOAuth2User implements OAuth2User {

    /**
     * The OAuth2User.
     */
    private OAuth2User oAuth2User;

    public CustomOAuth2User(OAuth2User user) {
        this.oAuth2User = user;
    }

    @Override
    public Map<String, Object> getAttributes() {
        return oAuth2User.getAttributes();
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return oAuth2User.getAuthorities();
    }

    @Override
    public String getName() {
        return oAuth2User.getAttribute("name");
    }
    
    public String getEmail() {
        return oAuth2User.getAttribute("email");
    }
}
