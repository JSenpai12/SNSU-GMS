const showSignupBtn = document.getElementById("show-signup");
const showLoginBtn = document.getElementById("show-login");

const loginContainer = document.getElementById("login-container");
const signupContainer = document.getElementById("signup-container");

// Hide signup by default
signupContainer.style.display = "none";

// Switch to signup
showSignupBtn.addEventListener("click", () => {
    loginContainer.style.display = "none";
    signupContainer.style.display = "block";
});

// Switch to login
showLoginBtn.addEventListener("click", () => {
    signupContainer.style.display = "none";
    loginContainer.style.display = "block";
});

