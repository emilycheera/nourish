// Show ratings chart button if patient has ratings data.
$("document").ready( () => {
    const pathArray = (window.location.pathname).split("/");
    const patientId = pathArray[2];
    $.get(`/patient/${patientId}/recent-ratings.json`, (res) => {
        if (res.dropdown.dropdown_dates.length != 0) {
            $(".ratings-chart-btn").show()
        }
    });
});