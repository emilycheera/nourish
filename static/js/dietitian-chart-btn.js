// Disable ratings chart button, enable tooltip if patient has no ratings data.
$("document").ready( () => {
    const pathArray = (window.location.pathname).split("/");
    const patientId = pathArray[2];
    $.get(`/patient/${patientId}/recent-ratings.json`, (res) => {
        if (jQuery.isEmptyObject(res)) {
            $(".ratings-chart-btn").prop("disabled", true);
            $("#disabled-btn-tooltip").attr("title", "Patient has no ratings data.").tooltip();

        };
    });
});