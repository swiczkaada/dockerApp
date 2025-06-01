document.addEventListener("DOMContentLoaded", function () {
    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_new_password');
    const messageDiv = document.getElementById('password-match-message');

    function checkPasswordMatch() {
        const pass = newPasswordInput.value;
        const confirm = confirmPasswordInput.value;

        if (!confirm) {
            messageDiv.classList.add('hidden');
            messageDiv.textContent = '';
            return;
        }

        if (pass === confirm) {
            messageDiv.textContent = 'Les mots de passe correspondent';
            messageDiv.classList.remove('hidden', 'text-red-600');
            messageDiv.classList.add('text-green-600');
        } else {
            messageDiv.textContent = 'Les mots de passe ne correspondent pas';
            messageDiv.classList.remove('hidden', 'text-green-600');
            messageDiv.classList.add('text-red-600');
        }
    }

    newPasswordInput.addEventListener('input', checkPasswordMatch);
    confirmPasswordInput.addEventListener('input', checkPasswordMatch);

    // Toggle password visibility
    const toggleBtn = document.getElementById("togglePassword");
    const eyeIcon = document.getElementById("eyeIcon");

    toggleBtn.addEventListener("click", () => {
        const isPassword = newPasswordInput.getAttribute("type") === "password";
        newPasswordInput.setAttribute("type", isPassword ? "text" : "password");
        eyeIcon.src = isPassword ? "/media/img/blob_disapointed.png" : "/media/img/blob_help.png";
    });
});
