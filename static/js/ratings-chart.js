
$(".ratings-chart-btn").on("click", (evt) => {
    evt.preventDefault();

    const patientId = evt.target.dataset.patientId;

    $.get(`/patient/${patientId}/weekly-ratings.json`, (res) => {
      const hungerData = [];
      for (const post of res.data.hunger) {
        hungerData.push({x: post.meal_time, y: post.hunger_rating});
    }

      const fullnessData = [];
      for (const post of res.data.fullness) {
        fullnessData.push({x: post.meal_time, y: post.fullness_rating});
    }
      const satisfactionData = [];
      for (const post of res.data.satisfaction) {
        satisfactionData.push({x: post.meal_time, y: post.satisfaction_rating});
  }

  Chart.defaults.global.defaultFontFamily = "Roboto";
  Chart.defaults.global.legend.position = 'bottom';
  new Chart(
    $("#ratings-chart"),
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
        },
    }
    }
  );
});
});

