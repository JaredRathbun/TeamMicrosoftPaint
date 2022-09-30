function sendLogin() {
    const email = document.getElementById("emailField").value;
    const password = document.getElementById('passwordField').value;

    
    // Send the login request here.

    // If successful, clear the login fields and prompt for an OTP.
    const loginDiv = document.getElementById('login-container');
    loginDiv.innerHTML = '';

    loginDiv.innerHTML = `
        <div class="col-lg-6 d-none d-lg-flex">
        <img class="flex-grow-1 bg-login-image" style="background-image: url('../static/img/mack.gif');">
        </div>
        <div class="col-lg-6 ">
            <div class="p-5" id="login-container">
                <div class="text-center">
                    <h4 class="text-dark mb-4">2-Factor Authentication</h4>
                </div>
                <h3>Please enter your OTP (One Time Passcode) sent to your email.</h3>
                <form class="user">
                    <div class="mb-3"><input class="form-control form-control-user" type="email" id="emailField" aria-describedby="emailHelp" placeholder="Enter Email Address..." name="email"></div>
                    <div class="mb-3"><input class="form-control form-control-user" type="password" id="passwordField" placeholder="Password" name="password"></div>
                    <!-- <div class="mb-3">
                        <div class="custom-control custom-checkbox small">
                            <div class="form-check"><input class="form-check-input custom-control-input" type="checkbox" id="formCheck-1"><label class="form-check-label custom-control-label" for="formCheck-1">Remember Me</label></div>
                        </div>
                    </div>-->
                    <p class="text-danger text-center" style="visibility: hidden;">Invalid Email/Password</p>
                    <button class="btn btn-primary d-block btn-user w-100" type="submit" onclick="sendLogin()">Login</button> 
                    <hr><a class="btn btn-primary d-block btn-google btn-user w-100 mb-2" role="button"><i class="fab fa-google"></i>&nbsp; Login with Google</a>
                    <hr>
                </form>
                <div class="text-center"><a class="small" href="reset.html">Forgot Password?</a></div>
                <div class="text-center"><a class="small" href="register.html">Create an Account!</a></div>
            </div>
        </div>
    `;
}