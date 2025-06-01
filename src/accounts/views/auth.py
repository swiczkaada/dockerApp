from django.contrib import messages

from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from accounts.decorators import admin_or_superadmin_required
from activityLog.models import ActivityLog

User = get_user_model()

@admin_or_superadmin_required
def signup(request):
    """
    Handles user registration.
    - Validates input fields (email, username, password).
    - Ensures uniqueness of email and username.
    - Creates user account and logs the action.
    """
    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validate: email must be unique
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect("signup")

        # Validate: username must be unique
        if User.objects.filter(username=username).exists():
            messages.error(request,"Ce nom d\'utilisateur est déjà pris.")
            return redirect("signup")

        # Validate: password match
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect("signup")

        # Create user and log them in
        user = User.objects.create_user(email=email, username=username, password=password)
        login(request, user)

        # Log account creation
        ActivityLog.objects.create(
            user=user,
            action_type='USER_CREATED',
            description=f'User {username} enregistré avec succès.',
        )
        return redirect('index')
    return render(request, 'accounts/signup.html')

@login_required
def logout_user(request):
    """
    Logs out the currently authenticated user.
    """
    logout(request)
    return redirect('index')

def login_user(request):
    """
    Handles user login.
    - Authenticates with email and password.
    - Redirects to home on success.
    """
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get("password")

        # Authenticate using Django's built-in system
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Informations invalides")
    # GET request or failed login
    return render(request, 'accounts/login.html')