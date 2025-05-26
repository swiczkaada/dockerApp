from django.contrib.auth import get_user_model, login, logout, authenticate
from django.shortcuts import render, redirect

User = get_user_model()
# Create your views here.

def signup(request):
    if request.method == "POST":
        # Traiter le formulaire d'inscription
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = User.objects.create_user(username=username, password=password)

        login(request, user)
        return redirect('store-index')  # Rediriger vers la page d'accueil du store)
    return render(request, 'accounts/signup.html')

def logout_user(request):
        logout(request)
        return redirect('store-index')  # Rediriger vers la page d'accueil du store

def login_user(request):
    if request.method == "POST":
        # Traiter le formulaire de connexion
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('store-index')

    return render(request, 'accounts/login.html')