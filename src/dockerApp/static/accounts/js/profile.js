document.addEventListener("DOMContentLoaded", function () {
    let currentPage = 1;
    let query = '';
    let isLoading = false;
    let hasNext = true;

    const searchInput = document.getElementById('user-search');
    const userList = document.getElementById('user-list');

    function deleteUser(userEmail, liElement) {
        if (!confirm(`Voulez-vous vraiment supprimer l'utilisateur ${userEmail} ?`)) return;

        fetch('/delete-user/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: userEmail }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.success);
                // Supprime l'élément de la liste
                liElement.remove();
            } else if (data.error) {
                alert('Erreur : ' + data.error);
            }
        })
        .catch(() => alert('Erreur lors de la suppression.'));
    }
    function toggleUserStatus(email, button) {
        fetch('/toggle-user-status/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && typeof data.is_active !== 'undefined') {
                button.textContent = data.is_active ? 'Actif' : 'Inactif';
                button.classList.remove('border-green-500', 'text-green-600', 'border-red-500', 'text-red-600');
                if (data.is_active) {
                    button.classList.add('border-green-500', 'text-green-600');
                } else {
                    button.classList.add('border-red-500', 'text-red-600');
                }
            } else {
                alert(data.error || 'Erreur lors de la mise à jour du statut.');
            }
        })
        .catch(() => alert('Erreur réseau.'));
    }

    function loadUsers(reset = false) {
        if (isLoading || !hasNext) return;
        isLoading = true;

        fetch(`/search-users/?q=${encodeURIComponent(query)}&page=${currentPage}`)
            .then(response => response.json())
            .then(data => {
                if (reset) userList.innerHTML = '';

                data.results.forEach(user => {
                    const li = document.createElement('li');
                    li.className = 'flex items-center justify-between gap-4 py-2';

                    const userInfo = document.createElement('span');
                    userInfo.className = 'flex-1 text-gray-800 truncate';
                    userInfo.textContent = `${user.username} - ${user.email}`;
                    userInfo.classList.add('cursor-pointer', 'hover:underline');
                    userInfo.addEventListener('click', () => {
                        window.location.href = `/admin/users/${encodeURIComponent(user.username)}/`;
                    });

                    const btn = document.createElement('button');
                    btn.textContent = 'Supprimer';
                    btn.className = 'px-3 py-1 text-sm font-semibold text-red-600 border border-red-600 rounded-md hover:bg-red-600 hover:text-white transition';
                    btn.addEventListener('click', () => deleteUser(user.email, li));

                    const statusBtn = document.createElement('button');
                    statusBtn.textContent = user.is_active ? 'Actif' : 'Inactif';
                    statusBtn.className = `px-3 py-1 text-sm font-medium rounded-full border transition
                        ${user.is_active ? 'border-green-500 text-green-600' : 'border-red-500 text-red-600'}`;
                    statusBtn.addEventListener('click', () => toggleUserStatus(user.email, statusBtn));

                    li.appendChild(userInfo);
                    li.appendChild(btn);
                    li.appendChild(statusBtn);
                    userList.appendChild(li);
                });

                hasNext = data.has_next;
                isLoading = false;
                currentPage++;
            });
    }

    // Search on each keystroke
    searchInput.addEventListener('input', () => {
        query = searchInput.value.trim();
        currentPage = 1;
        hasNext = true;
        loadUsers(true);
    });

    // Infinite scrolling
    userList.addEventListener('scroll', () => {
        const scrollBottom = userList.scrollTop + userList.clientHeight >= userList.scrollHeight - 20;
        if (scrollBottom) {
            loadUsers();
        }
    });

    // Initial loading
    loadUsers();
});


// Simple script to manage section changes without reloading the page
document.querySelectorAll('#profile-menu .menu-item').forEach(item => {
    item.addEventListener('click', () => {
        // Remove active on all
        document.querySelectorAll('#profile-menu .menu-item').forEach(i => i.classList.remove('active'));
        // Ajouter active sur celui cliqué
        item.classList.add('active');

        // Hide all sections
        document.querySelectorAll('.section-content').forEach(sec => sec.classList.remove('active'));

        // Display the corresponding section
        const sectionId = item.getAttribute('data-section');
        document.getElementById(sectionId).classList.add('active');
    });
});