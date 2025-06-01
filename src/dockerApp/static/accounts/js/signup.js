document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("password");
    const bar = document.getElementById("password-bar");
    const text = document.getElementById("password-text");
    const feedback = document.getElementById("password-feedback");
    const toggleBtn = document.getElementById("togglePassword");
    const eyeIcon = document.getElementById("eyeIcon");

    passwordInput.addEventListener("input", () => {
        const val = passwordInput.value;

        if (val.length === 0) {
            feedback.classList.add("hidden");
            return;
        }

        feedback.classList.remove("hidden");

        let score = 0;
        if (val.length >= 8) score++;
        if (/[A-Z]/.test(val)) score++;
        if (/[a-z]/.test(val)) score++;
        if (/[0-9]/.test(val)) score++;
        if (/[^A-Za-z0-9]/.test(val)) score++;

        const levels = [
            { label: "Mot de passe très faible", color: "bg-red-500", width: "w-1/5", textColor: "text-red-600" },
            { label: "Faible", color: "bg-orange-400", width: "w-2/5", textColor: "text-orange-500" },
            { label: "Moyen", color: "bg-yellow-400", width: "w-3/5", textColor: "text-yellow-600" },
            { label: "Fort", color: "bg-green-400", width: "w-4/5", textColor: "text-green-600" },
            { label: "Robuste", color: "bg-green-600", width: "w-full", textColor: "text-green-700" },
        ];

        const level = levels[score > 0 ? score - 1 : 0];

        bar.className = `h-full ${level.width} ${level.color} transition-all duration-500 ease-in-out`;
        text.className = `mt-2 text-sm font-semibold ${level.textColor}`;
        text.textContent = level.label;
    });

    toggleBtn.addEventListener("click", () => {
        const isPassword = passwordInput.getAttribute("type") === "password";
        passwordInput.setAttribute("type", isPassword ? "text" : "password");

        eyeIcon.src = isPassword
            ? "/media/img/blob_disapointed.png"
            : "/media/img/blob_help.png";
    });
});
