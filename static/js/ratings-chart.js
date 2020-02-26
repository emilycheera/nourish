
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
  Chart.Legend.prototype.afterFit = function() {
    this.height = this.height + 10;
};
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
        title: {
            display: true,
            text: "Ratings for Week of [Date]",
            fontSize: 24,
            fontColor: "#212529",
            fontStyle: "normal",
        },
        scales: {
            xAxes: [{
                type: "time",
                time: {
                    tooltipFormat: "MMM D h:mm a"
                },
                distribution: "series"
            }],
        },
    }
    }
  );
});
});

