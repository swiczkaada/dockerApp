document.addEventListener("DOMContentLoaded", function () {
  const rawData = document.getElementById('chart-data');
  if (!rawData) return;

  const { labels30Days, data30Days, labels6Months, data6Months, topQRCodesLabels, topQRCodesData, hoursLabels, scansByHourData, activeCount, inactiveCount } = JSON.parse(rawData.textContent);

  new Chart(document.getElementById('scansByDayChart').getContext('2d'), {
    type: 'bar',
    data: {
      labels: labels30Days,
      datasets: [{
        label: 'Scans par jour',
        data: data30Days,
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: { scales: { y: { beginAtZero: true } }, responsive: true }
  });

  new Chart(document.getElementById('scansByMonthChart').getContext('2d'), {
    type: 'line',
    data: {
      labels: labels6Months,
      datasets: [{
        label: 'Scans par mois',
        data: data6Months,
        backgroundColor: 'rgba(255, 159, 64, 0.6)',
        borderColor: 'rgba(255, 159, 64, 1)',
        borderWidth: 2,
        fill: false,
        tension: 0.3
      }]
    },
    options: { scales: { y: { beginAtZero: true } }, responsive: true }
  });

  new Chart(document.getElementById('topQRCodesChart').getContext('2d'), {
    type: 'bar',
    data: {
      labels: topQRCodesLabels,
      datasets: [{
        label: 'Nombre de scans',
        data: topQRCodesData,
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      }]
    },
    options: { scales: { y: { beginAtZero: true } }, responsive: true }
  });

  new Chart(document.getElementById('scansByHourChart').getContext('2d'), {
    type: 'bar',
    data: {
      labels: hoursLabels,
      datasets: [{
        label: 'Scans par heure',
        data: scansByHourData,
        backgroundColor: 'rgba(153, 102, 255, 0.6)',
        borderColor: 'rgba(153, 102, 255, 1)',
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: { beginAtZero: true },
        x: { title: { display: true, text: 'Heure (0-23)' } }
      },
      responsive: true
    }
  });

  new Chart(document.getElementById('qrcodeActiveChart').getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Actifs', 'Inactifs'],
      datasets: [{
        data: [activeCount, inactiveCount],
        backgroundColor: [
          'rgba(54, 162, 235, 0.7)',
          'rgba(255, 99, 132, 0.7)'
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(255, 99, 132, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      cutout: '60%',
      animation: {
        animateRotate: true,
        animateScale: true
      },
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
});
