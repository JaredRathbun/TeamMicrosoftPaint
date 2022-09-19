package com.teammspaint.stemdatadashboard.auth.oauth;

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

import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;

/**
 * A Service for handling OAuth2 Users.
 * 
 * @author Jared Rathbun
 * 
 * Sourced from: https://www.codejava.net/frameworks/spring-boot/oauth2-login-with-google-example
 */
@Service
public class OAuth2UserService extends DefaultOAuth2UserService {
    
    /*
     * Loads the user from the {@code OAuth2UserRequest}.
     * 
     * @param userReq The {@code OAuth2UserRequest}.
     * @throws {@code OAuth2AuthenticationException} if an error occurs while 
     * attempting to obtain the user attributes from the UserInfo Endpoint
     */
    @Override
    public OAuth2User loadUser(OAuth2UserRequest userReq) throws 
            OAuth2AuthenticationException {
        return new CustomOAuth2User(super.loadUser(userReq));
    }
}
