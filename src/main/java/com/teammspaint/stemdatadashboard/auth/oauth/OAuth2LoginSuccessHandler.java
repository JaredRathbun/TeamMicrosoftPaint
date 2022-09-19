package com.teammspaint.stemdatadashboard.auth.oauth;

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import com.teammspaint.stemdatadashboard.repository.UserRepository;

@Component
public class OAuth2LoginSuccessHandler extends SimpleUrlAuthenticationSuccessHandler {
    
    @Autowired
    private UserRepository userRepo;

    @Override
	public void onAuthenticationSuccess(HttpServletRequest req, 
        HttpServletResponse res, Authentication auth) throws 
            IOException, ServletException {
		CustomOAuth2User oAuthUser = (CustomOAuth2User) auth.getPrincipal();
        
        // Attempt to add the user to the database.
        String email = oAuthUser.getEmail();
        String name = oAuthUser.getName();
        // Interact with userRepo here.

        // Keep authenticating.
        super.onAuthenticationSuccess(req, res, auth);
	}
}
