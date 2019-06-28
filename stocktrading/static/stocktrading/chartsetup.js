var ctx = document.getElementById('myChart').getContext('2d');
var current = "week"
var weekDataLine = [{% for i in historyData.week %}{{ i.c }},{% endfor %}]
var weekDataCandle = [{% for i in historyData.week %}{o:{{i.o}},c: {{i.c}}, h: {{i.h}}, l: {{i.l}}, t: "{{i.t}}"  },{% endfor %}]
var weekLabels =  [{% for i in labels.week %}"{{ i }}",{% endfor %}]

var yearDataLine = [{% for i in historyData.year %}{{ i.c }},{% endfor %}]
var yearDataCandle = [{% for i in historyData.year %}{o:{{i.o}},c: {{i.c}}, h: {{i.h}}, l: {{i.l}}, t: "{{i.t}}"  },{% endfor %}]
var yearLabels =  [{% for i in labels.year %}"{{ i }}",{% endfor %}]

var monthDataLine =  [{% for i in historyData.month %}{{ i.c }},{% endfor %}]
var monthDataCandle = [{% for i in historyData.month %}{o:{{i.o}},c: {{i.c}}, h: {{i.h}}, l: {{i.l}}, t: "{{i.t}}"  },{% endfor %}]
var monthLabels =  [{% for i in labels.month %}"{{ i }}",{% endfor %}]

var today = new Date()
var currentTime = luxon.DateTime.local()


for(i = 6; i >= 0;i--){
  weekDataCandle[i].t = currentTime.valueOf()
  currentTime = currentTime.minus({days:1})
}

currentTime = luxon.DateTime.local()

for(i = 29; i >= 0;i--){
  monthDataCandle[i].t = currentTime.valueOf()
  currentTime = currentTime.minus({days:1})
}

currentTime = luxon.DateTime.local()
trimmedYearData = []
for(i = 249; i >= 0;i--){
  yearDataCandle[i].t = currentTime.valueOf()
  trimmedYearData.unshift(yearDataCandle[i])
  currentTime = currentTime.minus({days:1})
}
yearDataCandle = trimmedYearData

var weekData = weekDataLine
var monthData = monthDataLine
var yearData = yearDataLine
var chartOptionsLine =  {
      responsive:true,
      maintainAspectRatio:false,
        scales: {
            xAxes: [{
                ticks: {
                  autoSkip: true,
                  maxTicksLimit: 20
                }
            }],
            yAxes: [{
                ticks: {
                    beginAtZero: false
                }
            }]
        },
        tooltips: {
            callbacks: {
                label: function(tooltipItem, data) {
                    var label = "Price";

                    if (label) {
                        label += ': $';
                    }
                    label += tooltipItem.yLabel;
                    return label;
                }
            }
        },
        legend: {
            display: false,
            labels: {
                fontColor: 'rgb(255, 99, 132)'
            }
        },
         title: {
            display: true,
            text: 'Price History for {{stock.name}}',
            fontSize: 18
        }
    }

var chartOptionsCandle =  {
      responsive:true,
      maintainAspectRatio:false,
        scales: {
            xAxes: [{
                ticks: {
                  autoSkip: true,
                  maxTicksLimit: 20
                }
            }],
            yAxes: [{
                ticks: {
                    beginAtZero: false
                }
            }]
        },
        legend: {
            display: false,
            labels: {
                fontColor: 'rgb(255, 99, 132)'
            }
        },
         title: {
            display: true,
            text: 'Price History for {{stock.name}}',
            fontSize: 18
        }
    }

var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels:  weekLabels,
        datasets: [{
            label: 'Price',
            data: weekData,
            backgroundColor: 'rgb(95,120,138,0.1)',
            borderColor: 'rgba(95,120,138,0.8)',
            borderWidth: 1
        }]
    },
    options:chartOptionsLine
});
$("#week").click(function (){
  current = "week"
  var data = myChart.config.data;
    data.datasets[0].data = weekData;
    data.labels = weekLabels;
    myChart.update();
});
$("#month").click(function (){
    current = "month"
    var data = myChart.config.data;
    data.datasets[0].data = monthData;
    data.labels = monthLabels;
    myChart.update();
});
$("#year").click(function (){
  current = "year"
  var data = myChart.config.data;
    data.datasets[0].data = yearData;
    data.labels = yearLabels;
    myChart.update();
});
$("#candlestick").click(function (){
  weekData = weekDataCandle
  monthData = monthDataCandle
  yearData = yearDataCandle

  var currentData = weekDataCandle
  if(current == "month") currentData = monthDataCandle
  if(current == "year") currentData = yearDataCandle
  myChart.destroy();
  myChart = new Chart(ctx, {
    type: 'candlestick',
    data: {
        datasets: [{
            data: currentData,
            backgroundColor: 'rgb(95,120,138,0.1)',
            borderColor: 'rgba(95,120,138,0.8)',
            borderWidth: 1
        }]
    },
    options:chartOptionsCandle
  })
});
$("#line").click(function (){
  weekData = weekDataLine
  monthData = monthDataLine
  yearData = yearDataLine

  var currentData = weekData
  var currentLabel = weekLabels
  if(current == "month"){
    currentData = monthDataLine
    currentLabel = monthLabels
  } 
  if(current == "year"){
    currentData = yearDataLine
    currentLabel = yearLabels
  } 

  myChart.destroy();
  myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels:  currentLabel,
        datasets: [{
            label: 'Price',
            data: currentData,
            backgroundColor: 'rgb(95,120,138,0.1)',
            borderColor: 'rgba(95,120,138,0.8)',
            borderWidth: 1
        }]
    },
    options:chartOptionsLine
  })
});