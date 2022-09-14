package com.teammspaint.stemdatadashboard.oauth;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;

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

import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;


@Configuration
public class SecurityConfig {
    
    @Autowired
    private OAuth2UserService oAuthUserService;

    @Autowired
    private OAuth2LoginSuccessHandler oAuth2LoginSuccessHandler;

    @Bean 
    protected SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        // Authorize requests from /login and /oauth.
        http.authorizeRequests().antMatchers("/", "/login", "/oauth/**")
            .permitAll().anyRequest().authenticated().and().formLogin()
            .permitAll().and().oauth2Login().loginPage("/login")
            .userInfoEndpoint().userService(oAuthUserService).and()
            .successHandler(oAuth2LoginSuccessHandler);

        // Add headers.
        http.headers().frameOptions().sameOrigin();

        // Build the http object.
        return http.build();
    }

}
