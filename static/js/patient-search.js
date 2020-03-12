$(document).ready(function() {
    $(".patient-search").select2({
        placeholder: "",
        allowClear: true,
        theme: "bootstrap"
    });
    $("#patient").on("select2:select", function (e) {
        window.location.replace(e.params.data.id);
    });
});


$(document).ready(function() {
    $(".patient-search").select2({
        placeholder: "Patient Search",
        allowClear: true,
        theme: "bootstrap"
    });
    $("#patient-mobile").on("select2:select", function (e) {
        window.location.replace(e.params.data.id);
    });
});

