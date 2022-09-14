package com.teammspaint.stemdatadashboard.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class Endpoints {
    
    @GetMapping("/login")
    public String getLogin() {
        return "login";
    }
}
