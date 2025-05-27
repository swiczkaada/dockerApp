# accounts/api/views.py
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate, login, logout

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def api_signup(request):
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')

    if not (email and username and password):
        return Response({"error": "Tous les champs sont requis."}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Cet email est déjà utilisé."}, status=400)

    user = User.objects.create_user(email=email, username=username, password=password)
    login(request, user)
    return Response({
        "message": "Inscription réussie",
        "user": {"username": user.username, "email": user.email}
    }, status=201)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    print("Login attempt with data:", request.data)  # Debugging line
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(request, email=email, password=password)
    if user:
        login(request, user)
        return Response({
            "message": "Connexion réussie",
            "user": {"username": user.username, "email": user.email}
        })
    return Response({"error": "Identifiants invalides."}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    logout(request)
    return Response({"message": "Déconnexion réussie."})


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def api_profile(request):
    user = request.user

    if request.method == 'PUT':
        user.email = request.data.get('email', user.email)
        user.username = request.data.get('username', user.username)
        user.save()

    return Response({
        "username": user.username,
        "email": user.email,
        "date_joined": user.date_joined,
        "last_login": user.last_login,
    })
