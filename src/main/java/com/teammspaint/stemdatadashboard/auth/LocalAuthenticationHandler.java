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

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.security.web.authentication.logout.LogoutSuccessHandler;
import org.springframework.stereotype.Component;

@Component("Local Auth Handler")
public class LocalAuthenticationHandler implements AuthenticationSuccessHandler,
    LogoutSuccessHandler {

    @Autowired
    private ActiveUserStore activeUserStore;

    @Override
    public void onAuthenticationSuccess(HttpServletRequest req, 
        HttpServletResponse res, Authentication auth) throws  IOException, 
            ServletException {
        HttpSession session = req.getSession(false);
        if (session != null) {
            LoggedUser usr = new LoggedUser(auth.getName(), 
                activeUserStore);
            session.setAttribute("user", usr);
        }
    }

    @Override
    public void onLogoutSuccess(HttpServletRequest req, HttpServletResponse res, 
        Authentication auth) throws IOException, ServletException {
        HttpSession session = req.getSession();
        if (session != null) {
            session.removeAttribute("user");
        }
    }
}
