
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
                alert(res);
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
