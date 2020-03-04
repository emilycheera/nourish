
// Set default font family and legend position for all charts.
Chart.defaults.global.defaultFontFamily = "Roboto";
Chart.defaults.global.legend.position = "bottom";

// Set configuration for all charts.
const config_chart = (hungerData, fullnessData, satisfactionData) => {
    const config =   
        {   
            type: "line",
            data: {
                datasets: [{
                    label: "Hunger Rating",
                    data: hungerData,
                    lineTension: 0,
                    backgroundColor: "#FFB561",
                    borderColor: "#FFB561",
                    fill: false,
                    borderWidth: 4,
                    pointBackgroundColor: "#FFB561"
                }, {
                    label: "Fullness Rating",
                    data: fullnessData,
                    lineTension: 0,
                    backgroundColor: "#E87E07",
                    borderColor: "#E87E07",
                    fill: false,
                    borderWidth: 4,
                    pointBackgroundColor: "#E87E07"
                }, {
                    label: "Satisfaction Rating",
                    data: satisfactionData,
                    lineTension: 0,
                    backgroundColor: "#904C00",
                    borderColor: "#904C00",
                    fill: false,
                    borderWidth: 4,
                    pointBackgroundColor: "#904C00"
                    }]
                },
            options: {
                legend: {
                    labels: {
                        padding: 30,
                    }
                },
                scales: {
                    xAxes: [{
                        type: "time",
                        time: {
                            tooltipFormat: "MMM D  h:mma",
                            displayFormats: {
                               "millisecond": "MMM DD",
                               "second": "MMM DD",
                               "minute": "MMM DD",
                               "hour": "MMM DD",
                               "day": "MMM DD",
                               "week": "MMM DD",
                               "month": "MMM DD",
                               "quarter": "MMM DD",
                               "year": "MMM DD",
                            }
                        },
                        distribution: "series"
                    }],
                    yAxes: [{
                        ticks: {
                            min: 0,
                            suggestedMax: 10,
                        }
                    }]
                },
            }
        }
    return config;
}


const getModal = (res) => {
    const postTimeStamp = (moment(res.post.time_stamp).format("MMM D, YYYY [at] h:mm A"));
    const imgPath = (res.post.img_path) ? `<img src="${res.post.img_path}" class="post-image">` : "";
    const mealTime = (moment(res.post.meal_time).format("MMM D, YYYY [at] h:mm A"));
    const hunger = (res.post.hunger) ? `<p><b>Hunger:</b> ${res.post.hunger}</p>` : "";
    const fullness = (res.post.fullness) ? `<p><b>Fullness:</b> ${res.post.fullness}</p>` : "";
    const satisfaction = (res.post.satisfaction) ? `<p><b>Satisfaction:</b> ${res.post.satisfaction}</p>` : "";
    const mealNotes = (res.post.meal_notes) ? `<p><b>Additional Notes:</b>$ {res.post.meal_notes}</p>` : "";
    let commentDiv;

    if (res.comments) {
        commentDiv = `<div class="border-top">
                      </div>
                        <div id="comment-div">
                           <div id="comments-for-${res.post.post_id}">`;

        for (const comment of Object.values(res.comments)) {
            const commentId = comment.comment_id;
            const commentTimeStamp = (moment(comment.time_stamp).format("MMM D, YYYY [at] h:mm A"));
            const deleteCommentBtn = (comment.is_author) ? `<button class="modal-delete-comment-btn btn btn-link" data-comment-id="${commentId}">Delete</button>` : "";

            commentDiv += `<div id="comment-${commentId}">
                                <p class="comment-body">
                                    <b>${comment.author_fname} ${comment.author_lname}</b>
                                    ${comment.comment_body}
                                </p>
                                <p class="comment-time">
                                    ${commentTimeStamp}${comment.edited}
                                    ${deleteCommentBtn}
                                </p>
                            </div>`;
        };
        commentDiv += "</div></div>";
    };

    const modalHTML = `<div class="modal" id="post-modal" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">
                          <div class="modal-dialog modal-dialog-centered" role="document">
                            <div class="modal-content">
                              <div class="modal-body">
                                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                  <span aria-hidden="true">&times;</span>
                                </button>
                                <div class="post-container">
                                    <div class="post-content">
                                        <a href="/patient/${res.patient.patient_id}/account" class="post-author">
                                            ${res.patient.fname} ${res.patient.lname}
                                        </a>
                                        <p class="post-time">${postTimeStamp}${res.post.edited}</p>
                                    </div>
                                        ${imgPath}
                                    <div class="post-content">
                                        <div class="post-fields">
                                            <p><b>Meal Time:</b> ${mealTime}</p>
                                            <p><b>Setting:</b> ${res.post.meal_setting}</p>
                                            <p><b>Thoughts, Emotions, Behaviors:</b> ${res.post.TEB}</p>
                                             ${hunger}
                                             ${fullness}
                                             ${satisfaction}
                                             ${mealNotes}
                                        </div>
                                        ${commentDiv}
                                        <form class="modal-add-comment-form" id="add-comment-form-${res.post.post_id}" data-post-id="${res.post.post_id}">
                                            <textarea class="comment-box" required name="comment" placeholder="Write a comment..."></textarea>
                                            <button type="submit" class="btn btn-outline-primary btn-sm btn-block">Submit Comment</button>
                                        </form>
                                    </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>`;

    return modalHTML;
};

// Disable ratings chart button, enable tooltip if patient has no ratings data.
$("document").ready( () => {
    const pathArray = (window.location.pathname).split("/");
    const patientId = pathArray[2];
    $.get(`/patient/${patientId}/recent-ratings.json`, (res) => {
        if (res.dropdown.dropdown_dates.length == 0) {
            $(".ratings-chart-btn").prop("disabled", true);
            $("#disabled-btn-tooltip").tooltip();
        };
    });
});

// When the ratings chart button is clicked, create "Ratings for Last 7 Days"
// chart and a dropdown so the user can get charts for previous weeks" ratings 
// data.
$(".ratings-chart-btn").on("click", (evt) => {
    evt.preventDefault();
    const patientId = evt.target.dataset.patientId;
    window.history.pushState("object or string", "", `/patient/${patientId}/ratings-chart`);
    
    $.get(`/patient/${patientId}/recent-ratings.json`, (res) => {
        const hungerData = [];
        for (const post of res.data.hunger) {
            hungerData.push({x: post.meal_time, y: post.rating});
        }
        const fullnessData = [];
        for (const post of res.data.fullness) {
            fullnessData.push({x: post.meal_time, y: post.rating});
        }
        const satisfactionData = [];
        for (const post of res.data.satisfaction) {
            satisfactionData.push({x: post.meal_time, y: post.rating});
        }
  
        // Get option elements for dropdown.
        let dateOptions;
        for (date of res.dropdown.dropdown_dates) {
            const formattedDate = (moment(date).format("MMM D, YYYY"));
            dateOptions += `<option value="${date}">${formattedDate}</option>`;
        };

        $("#patient-content").replaceWith(`<div id="patient-content">
                <form class="chart-date-form mb-5 mr-auto" data-patient-id="${patientId}">
                    <label for="chart-date-select" class="sr-only">
                        See ratings for previous weeks:
                    </label>
                    <div class="input-group input-group-sm chart-date-div">
                    <div class="input-group-prepend">
                        <span class="input-group-text">See ratings for previous weeks:</span>
                    </div>
                    <select name="chart-date" id="chart-date-select" class="custom-select">
                        <option value="" disabled selected hidden>Select a Date</option>
                        ${dateOptions}
                    </select>
                    <div class="input-group-append">
                        <button type="submit" class="btn btn-outline-secondary">Get Chart</button>
                    </div>
                    </div>
                </form>
                <div id="chart-div">
                    <h4>
                        Ratings for the Last 7 Days
                    </h4>
                    <p>
                        Hover over a point to see more information about a 
                        rating. Click on a point to see the patient's post.
                    </p>
                    <canvas id="ratings-chart-recent" class="ratings-chart" width="800" 
                        height="500"></canvas>
                </div>
            </div>
            <div id="post-modal-div">
            </div>`
        );
        
        const config = config_chart(hungerData, fullnessData, satisfactionData);

        const ratingsChart = new Chart($("#ratings-chart-recent"), config);

        // When a user clicks on a point on the chart, get data for that point
        // and display a modal window with the post for that data.
        $("#ratings-chart-recent").on("click", (evt) => {
            var firstPoint = ratingsChart.getElementAtEvent(evt)[0];

            if (firstPoint) {
                var label = ratingsChart.data.datasets[firstPoint._datasetIndex].label;
                var value = ratingsChart.data.datasets[firstPoint._datasetIndex].data[firstPoint._index];

                const postData = {
                    ratingLabel: label,
                    postDatetime: value.x,
                    ratingValue: value.y
                };

                $.get(`/patient/${patientId}/get-post.json`, postData, (res) => {
                    $("#post-modal-div").html(getModal(res));
                    $("#post-modal").modal();
                });
            };
        });
    });
});


// When a user submits the chart-date-form dropdown, create a chart and 
// display a chart for the selected dates.
$("body").on("submit", "form.chart-date-form", (evt) => {
    evt.preventDefault();

    const patientId = evt.target.dataset.patientId;
    const formValues = $(".chart-date-form").serialize();

    $.get(`/patient/${patientId}/past-ratings.json`, formValues, (res) => {
        const hungerData = [];
        for (const post of res.data.hunger) {
            hungerData.push({x: post.meal_time, y: post.rating});
        }
        const fullnessData = [];
        for (const post of res.data.fullness) {
            fullnessData.push({x: post.meal_time, y: post.rating});
        }
        const satisfactionData = [];
        for (const post of res.data.satisfaction) {
            satisfactionData.push({x: post.meal_time, y: post.rating});
        }

        const searchStartDate = (moment(res.data.chart_start_date)
                                 .format("MMM D, YYYY"));

        $("#chart-div").replaceWith(`<div id="chart-div">
                                    <h4>
                                        Ratings for Week of ${searchStartDate}
                                    </h4>
                                    <p>
                                        Hover over a point to see more information about a 
                                        rating. Click on a point to see the patient's post.
                                    </p>
                                    <canvas id="ratings-chart-previous" class="ratings-chart" width="800" 
                                        height="500"></canvas>
                                    </div>`);
      
        const config = config_chart(hungerData, fullnessData, satisfactionData);

        const ratingsChart = new Chart($("#ratings-chart-previous"), config);

        // When a user clicks on a point on the chart, get data for that point
        // and display a modal window with the post for that data.
        $("#ratings-chart-previous").on("click", (evt) => {
            var firstPoint = ratingsChart.getElementAtEvent(evt)[0];

            if (firstPoint) {
                var label = ratingsChart.data.datasets[firstPoint._datasetIndex].label;
                var value = ratingsChart.data.datasets[firstPoint._datasetIndex].data[firstPoint._index];

                const postData = {
                    ratingLabel: label,
                    postDatetime: value.x,
                    ratingValue: value.y
                };

                $.get(`/patient/${patientId}/get-post.json`, postData, (res) => {
                    $("#post-modal-div").html(getModal(res));
                    $("#post-modal").modal();
            });
            };
        });
    });
});


const getCommentDiv = (res) => {
    const timeStamp = (moment(res.comment.time_stamp).format("MMM D, YYYY [at] h:mm A"));
    return `<div id="comment-${res.comment.comment_id}">
                <p class="comment-body">
                    <b>${res.user.fname} ${res.user.lname}:</b> 
                    ${res.comment.comment_body}
                </p>
                <p class="comment-time">
                    ${timeStamp}${res.comment.edited}
                    <button class="modal-delete-comment-btn btn btn-link" data-comment-id="${res.comment.comment_id}">Delete</button>
                </p>
            </div>`;
}


$("body").on("submit", "form.modal-add-comment-form", (evt) => {
    evt.preventDefault();
    const postId = evt.target.dataset.postId;
    const formValues = $(`#add-comment-form-${postId}`).serialize();
    $(`#add-comment-form-${postId}`)[0].reset();
    $.post(`/post/${postId}/add-comment.json`, formValues, (res) => {
        $(`#comments-for-${postId}`).append(getCommentDiv(res));
    });
});


$("body").on("click", "button.modal-delete-comment-btn", (evt) => {
    result = window.confirm("Are you sure you want to delete this comment?");

    if (result) {
        const commentId = evt.target.dataset.commentId;
        $.post("/delete-comment", { comment: commentId }, () => {
            $(`#comment-${commentId}`).hide()
        });
    };
});
