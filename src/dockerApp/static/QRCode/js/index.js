document.addEventListener('DOMContentLoaded', function () {
  const searchForm = document.getElementById('searchForm');
  const qrList = document.getElementById('qrList');

  searchForm.addEventListener('submit', function (event) {
    event.preventDefault();
    const query = searchForm.query.value.trim();
    const searchType = searchForm.search_type.value;
    const status = searchForm.status.value;
    if (!query || !searchType) {
      qrList.innerHTML = '<li class="p-4 text-red-500">Veuillez choisir un critère et entrer une valeur.</li>';
      return;
    }
    loadQRCode(query, searchType, status);
  });

  function loadQRCode(query, type, status) {
    fetch(`/qrcode/search/?query=${encodeURIComponent(query)}&type=${type}&status=${status}`)
      .then(response => response.json())
      .then(data => {
        qrList.innerHTML = '';
        if (data.length > 0) {
          data.forEach(qrcode => {
            const li = document.createElement('li');
            li.className = 'p-4 bg-white rounded-xl shadow-sm hover:bg-blue-50 transition cursor-pointer space-y-2';

            const container = document.createElement('div');
            container.className = 'flex flex-col md:flex-row md:items-center md:justify-between gap-2';

            const left = document.createElement('div');
            left.className = 'flex flex-col space-y-1 md:max-w-md';

            const title = document.createElement('span');
            title.className = 'text-lg font-semibold text-blue-900 hover:text-blue-600 transition';
            title.textContent = qrcode.title || 'Sans titre';
            title.addEventListener('click', () => {
              window.location.href = 'qrcode/' + qrcode.uuid;
            });

            const url = document.createElement('a');
            url.href = qrcode.target_url;
            url.textContent = qrcode.target_url;
            url.className = 'text-sm text-blue-600 hover:underline break-words';
            url.target = '_blank';

            left.appendChild(title);
            left.appendChild(url);

            const right = document.createElement('div');
            right.className = 'flex flex-col items-start md:items-end space-y-1 text-sm';

            const scanCount = document.createElement('span');
            scanCount.className = 'text-gray-500';
            scanCount.textContent = `Scans : ${qrcode.scan_count}`;

            const status = document.createElement('span');
            status.className = qrcode.is_active
              ? 'inline-flex items-center px-2 py-1 text-xs font-semibold text-green-700 bg-green-100 rounded-full'
              : 'inline-flex items-center px-2 py-1 text-xs font-semibold text-red-700 bg-red-100 rounded-full';
            status.textContent = qrcode.is_active ? 'Actif' : 'Inactif';

            const viewBtn = document.createElement('a');
            viewBtn.href = 'qrcode/' + qrcode.uuid;
            viewBtn.textContent = 'Voir';
            viewBtn.className = 'inline-block mt-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-1 rounded-lg text-xs';

            right.appendChild(scanCount);
            right.appendChild(status);
            right.appendChild(viewBtn);

            container.appendChild(left);
            container.appendChild(right);
            li.appendChild(container);
            qrList.appendChild(li);
          });
        } else {
          qrList.innerHTML = '<li class="p-4 text-gray-500">Aucun QR Code trouvé.</li>';
        }
      })
      .catch(error => {
        console.error('Erreur lors de la recherche de QR Codes:', error);
        qrList.innerHTML = '<li class="p-4 text-red-500">Erreur lors de la recherche. Veuillez réessayer.</li>';
      });
  }
});
