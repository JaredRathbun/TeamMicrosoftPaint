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

import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.Objects;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.slf4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import com.teammspaint.stemdatadashboard.service.UserService;

@Controller
public class AuthEndpoints {

    /**
     * The logger used for printing to the terminal.
     */
    private static final Logger log = LoggerFactory.getLogger(AuthEndpoints
        .class);

    @Autowired
    private UserService userService;

    @Autowired
    private ActiveUserStore activeUserStore;

    /**
     * Checks to see if a user is logged in and renders the dashboard if the are.
     * If the user is not logged in, then the login page is rendered.
     * 
     * @param req The HTTP Request Server.
     * @return Either the dashboard or login template.
     */
    @GetMapping("/")
    public String dashboardOrLogin(HttpServletRequest req) {
        return (req.getSession().getAttribute("user") != null) ? 
            "dashboard" : "login";
    }

    /**
     * Renders the login page.
     * 
     * @return The login template.
     */
    @GetMapping("/login")
    public String getLogin() {
        return "login";
    }

    /**
     * Handles a user log in.
     * @return 
     */
    @PostMapping("/login")
    public String postLogin(@RequestBody Map<String, Object> body, 
        HttpServletRequest req, HttpServletResponse res) {
        assert (body != null) && (req != null);

        String email = (String) Objects.requireNonNull(body.get("email"), 
            "Email must not be null.");
        String password = (String) Objects.requireNonNull(body.get("password"), 
            "Password must not be null.");

        if (userService.verifyPassword(email, password)) {
            if (userService.isAdmin(email)) {
                res.setStatus(202);
                // Generate the OTP and email it.
                return null;
            } else {
                // Redirect the user to the dashboard.
                return "redirect:/dashboard";
            }
        } else {
            // User is not authorized, send 401.
            res.setStatus(401);
            return null;
        }

        
    }

    /**
     * Renders the reset page.
     * 
     * @return The reset template.
     */
    @GetMapping("/reset")
    public String getReset() {
        return "reset";
    }

    /**
     * Renders the register page.
     * 
     * @return The register template.
     */
    @GetMapping("/register") 
    public String getRegister() {
        return "register";
    }
}
