document.addEventListener('DOMContentLoaded', () => {
  const rawData = document.getElementById('chart-data');
  if (!rawData) return;

  const { labels, data, hour_labels, hour_data } = JSON.parse(rawData.textContent);

  // Chart 1 : Scans sur 7 jours
  const scansCtx = document.getElementById('scansChart')?.getContext('2d');
  if (scansCtx) {
    new Chart(scansCtx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Nombre de scans',
          data: data,
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        scales: { y: { beginAtZero: true } }
      }
    });
  }

  // Chart 2 : Scans par heure
  const hourCtx = document.getElementById('hourChart')?.getContext('2d');
  if (hourCtx) {
    new Chart(hourCtx, {
      type: 'line',
      data: {
        labels: hour_labels,
        datasets: [{
          label: 'Scans par heure',
          data: hour_data,
          backgroundColor: 'rgba(153, 102, 255, 0.4)',
          borderColor: 'rgba(153, 102, 255, 1)',
          borderWidth: 2,
          fill: true,
          tension: 0.3,
          pointRadius: 3
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: { beginAtZero: true },
          x: { title: { display: true, text: 'Heure (0 à 23h)' } }
        }
      }
    });
  }
});
