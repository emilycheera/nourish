
Chart.defaults.global.defaultFontFamily = "Roboto";
Chart.defaults.global.legend.position = 'bottom';

const config_chart = (hungerData, fullnessData, satisfactionData) => {
    const config =   
        {   
            type: "line",
            data: {
                datasets: [{
                    label: "Hunger Rating",
                    data: hungerData,
                    backgroundColor: "#FFB561",
                    borderColor: "#FFB561",
                    fill: false,
                    borderWidth: 4,
                    pointBackgroundColor: "#FFB561"
                }, {
                    label: "Fullness Rating",
                    data: fullnessData,
                    backgroundColor: "#E87E07",
                    borderColor: "#E87E07",
                    fill: false,
                    borderWidth: 4,
                    pointBackgroundColor: "#E87E07"
                }, {
                    label: "Satisfaction Rating",
                    data: satisfactionData,
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
                               'millisecond': 'MMM DD',
                               'second': 'MMM DD',
                               'minute': 'MMM DD',
                               'hour': 'MMM DD',
                               'day': 'MMM DD',
                               'week': 'MMM DD',
                               'month': 'MMM DD',
                               'quarter': 'MMM DD',
                               'year': 'MMM DD',
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


<!-- Modal -->

const getModal = (res) => {

    const imgPath = (res.post.img_path) ? `<img src="${res.post.img_path}" class="post-image">` : "";
    const hunger = (res.post.hunger) ? `<p><b>Hunger:</b>${res.post.hunger}</p>` : "";
    const fullness = (res.post.fullness) ? `<p><b>Fullness:</b>${res.post.fullness}</p>` : "";
    const satisfaction = (res.post.satisfaction) ? `<p><b>Satisfaction:</b>${res.post.satisfaction}</p>` : "";
    const mealNotes = (res.post.meal_notes) ? `<p><b>Additional Notes:</b>${res.post.meal_notes}</p>` : "";

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
                                        <p class="post-time">${res.post.time_stamp}${res.post.edited}</p>
                                    </div>
                                        ${imgPath}
                                    <div class="post-content">
                                        <div class="post-fields">
                                            <p><b>Meal Time:</b> ${res.post.meal_time}</p>
                                            <p><b>Setting:</b> ${res.post.meal_setting}</p>
                                            <p><b>Thoughts, Emotions, Behaviors:</b> ${res.post.TEB}</p>
                                             ${hunger}
                                             ${fullness}
                                             ${satisfaction}
                                             ${mealNotes}
                                        </div>
                                    </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>`;

    return modalHTML;
}




$(".ratings-chart-btn").on("click", (evt) => {
    evt.preventDefault();

    const patientId = evt.target.dataset.patientId;

    $.get(`/patient/${patientId}/weekly-ratings.json`, (res) => {
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
  
        const oneWeekAgo = (moment(res.data.one_week_ago).format("MMM D, YYYY"));

        const getDropdownHTML = (dropdownDates) => {
            let dateOptions;
            for (date of dropdownDates) {
                const formattedDate = (moment(date).format("MMM D, YYYY"));
                dateOptions += `<option value="${date}">${formattedDate}</option>`;
            };
            return dateOptions;
        };

        const dateOptions = getDropdownHTML(res.dropdown.dropdown_dates);

        $("#patient-content").replaceWith(`<div id="patient-content">
                <form class="chart-date-form mb-4" data-patient-id="${patientId}">
                    <label for="chart-date-select">
                        See ratings for previous weeks:
                    </label>
                    <select name="chart-date" id="chart-date-select">
                        ${dateOptions}
                    </select>
                    <button type="submit">Get Chart</button>
                </form>
                <div id="chart-div">
                    <h4>
                        Ratings for the Last 7 Days
                    </h4>
                    <p>
                        Hover over a point on the chart to view 
                        the rating’s value and the time it was posted.
                    </p>
                    <canvas id="ratings-chart" width="800" 
                        height="500"></canvas>
                </div>
            </div>
            <div id="post-modal-div">
            </div>`
        );
        
        const config = config_chart(hungerData, fullnessData, satisfactionData);

        const ratingsChart = new Chart($("#ratings-chart"), config);

        $("body").on("click", "canvas.chartjs-render-monitor", (evt) => {
            var firstPoint = ratingsChart.getElementAtEvent(evt)[0];

            if (firstPoint) {
                var label = ratingsChart.data.datasets[firstPoint._datasetIndex].label;
                var value = ratingsChart.data.datasets[firstPoint._datasetIndex].data[firstPoint._index];
            }

            const postData = {
                ratingLabel: label,
                postDatetime: value.x,
                ratingValue: value.y
            };

            $.get(`/patient/${patientId}/get-post.json`, postData, (res) => {
                $("#post-modal-div").html(getModal(res));
                $("#post-modal").modal();
            });
        });
    });
});



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

        const searchStartDate = (moment(res.data.search_start_date)
                                 .format("MMM D, YYYY"));

        $("#chart-div").replaceWith(`<div id="chart-div">
                                    <h4>
                                        Ratings for Week of ${searchStartDate}
                                    </h4>
                                    <p>
                                        Hover over a point on the chart to view the 
                                        rating’s value and the time it was posted.
                                    </p>
                                    <canvas id="ratings-chart" width="800" 
                                        height="500"></canvas>
                                       </div>`);
      
        const config = config_chart(hungerData, fullnessData, satisfactionData);

        const ratingsChart = new Chart($("#ratings-chart"), config);

    });
});
