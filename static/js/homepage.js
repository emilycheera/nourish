
// When a user clicks the patient button on a post,
// the patient login form is shown and the dietitian
// login form is hidden.
$("#patient-login-btn").on("click", (evt) => {
    $("#dietitian-login").hide();
    $("#patient-login").show();
});

// When a user clicks the dietitian button on a post,
// the dietitian login form is shown and the dietitian
// login form is hidden.
$("#dietitian-login-btn").on("click", (evt) => {
    $("#patient-login").hide();
    $("#dietitian-login").show();
});