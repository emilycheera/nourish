
$(".ratings-chart-btn").on("click", (evt) => {
    evt.preventDefault();

    const patientId = evt.target.dataset.patientId;

    $.get(`/patient/${patientId}/weekly-ratings.json`, (res) => {
      const hungerData = [];
      for (const dailyRating of res.data.hunger) {
        hungerData.push({x: dailyRating.meal_time, y: dailyRating.hunger_rating});
    }

      const fullnessData = [];
      for (const dailyRating of res.data.fullness) {
        fullnessData.push({x: dailyRating.meal_time, y: dailyRating.fullness_rating});
    }
      const satisfactionData = [];
      for (const dailyRating of res.data.satisfaction) {
        satisfactionData.push({x: dailyRating.meal_time, y: dailyRating.satisfaction_rating});
  }

  new Chart(
    $('#ratings-chart'),
    {
      type: "line",
      data: {
        datasets: [{
            label: "Hunger Rating",
            data: hungerData,
            lineTension: 0,
            backgroundColor: "#007bff",
            borderColor: "#007bff",
            fill: false,
            borderWidth: 4,
            pointBackgroundColor: "#007bff"
          }, {
            label: "Fullness Rating",
            data: fullnessData,
            lineTension: 0,
            backgroundColor: "#007bff",
            borderColor: "#007bff",
            fill: false,
            borderWidth: 4,
            pointBackgroundColor: "#007bff"
          }, {
            label: "Satisfaction Rating",
            data: satisfactionData,
            lineTension: 0,
            backgroundColor: "#007bff",
            borderColor: "#007bff",
            fill: false,
            borderWidth: 4,
            pointBackgroundColor: "#007bff"
          }]
      },
      options: {
        scales: {
            xAxes: [{
                type: 'time',
                distribution: 'series'
            }]
        },
        tooltips: {
          callbacks: {
            title: (tooltipItem) => {
              return moment(tooltipItem.label).format('MMM D');
            }
          }
        }
    }
    }
  );
});
});

