from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from activityLog.models import ActivityLog

User = get_user_model()
# Create your views here.

def signup(request):
    if request.method == "POST":
        # Traiter le formulaire d'inscription
        email = request.POST.get('email')
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(email=email).exists():
            return render(request, 'accounts/signup.html', {'error': 'Cet email est déjà utilisé.'})
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/signup.html', {'error': 'Ce nom d\'utilisateur est déjà pris.'})

        #Verifier si les mots de passe correspondent
        if password != confirm_password:
            return render(request, 'accounts/signup.html', {'error': 'Les mots de passe ne correspondent pas.'})

        # Créer l'utilisateur
        user = User.objects.create_user(email=email, username=username, password=password)
        login(request, user)

        # Register the log
        ActivityLog.objects.create(
            user=user,
            action_type='USER_CREATED',
            description=f'User {username} enregistré avec succès.',
        )
        return redirect('index')  # Rediriger vers la page d'accueil du store)
    return render(request, 'accounts/signup.html')

@login_required
def logout_user(request):
        logout(request)
        return redirect('index')  # Rediriger vers la page d'accueil du store

def login_user(request):
    if request.method == "POST":
        # Traiter le formulaire de connexion
        email = request.POST.get('email')
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('index')

    return render(request, 'accounts/login.html')