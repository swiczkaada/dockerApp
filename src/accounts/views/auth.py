from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

User = get_user_model()
# Create your views here.

def signup(request):
    if request.method == "POST":
        # Traiter le formulaire d'inscription
        email = request.POST.get('email')
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.create_user(email=email, username=username, password=password)
        login(request, user)
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