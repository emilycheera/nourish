$(document).ready(function() {
    $(".patient-search").select2();
    $("#patient").on("select2:select", function (e) {
        window.location.replace(e.params.data.id);
    });
});