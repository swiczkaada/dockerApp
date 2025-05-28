from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from accounts.models import CustomUser

User = get_user_model()
@login_required()
def profile(request):
    """
    Handles the profile view for the user.
    """
    if request.user.is_authenticated:

        # If the request method is POST, update the user's profile
        if request.method == "POST":
            user = request.user
            user.email = request.POST.get('email')
            user.username = request.POST.get('username')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.save()
            return redirect('profile')
        else :
            context = {}
            if request.user.is_admin() or request.user.is_superuser:
                search_query = request.GET.get('search', '')
                if search_query:
                    users = User.objects.filter(Q(username__icontains=search_query) |
                                                 Q(email__icontains=search_query)).exclude(id=request.user.id)
                else:
                    users = User.objects.exclude(id=request.user.id)
                context['users'] = users
            return render(request, 'accounts/profile.html', context)
    else:
        return redirect('login')  # Redirect to login if not authenticated

@login_required
def search_users(request):
    if not (request.user.is_authenticated and (request.user.is_admin() or request.user.is_super_admin())):
        return JsonResponse({'results': []}, status=403)

    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    #Exclude the current user, admin and superuser on the search results,
    users_qs = User.objects.exclude(id=request.user.id).exclude(permission__in=[2, 3])
    if query:
        users_qs = users_qs.filter(Q(username__istartswith=query) | Q(email__istartswith=query))

    paginator = Paginator(users_qs, 5)
    users_page = paginator.get_page(page)

    data = [{
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active,
    } for user in users_page]

    return JsonResponse({
        'results': data,
        'has_next': users_page.has_next()
    })

@csrf_exempt  # désactivé CSRF pour cette API (à utiliser avec prudence)
@require_POST
@login_required
def delete_user_view(request):
    if not (request.user.is_admin() or request.user.is_super_admin()):
        return JsonResponse({'error': 'Permission refusée.'}, status=403)

    try:
        data = json.loads(request.body)
        email = data.get('email')
        if not email:
            return JsonResponse({'error': "Email manquant."}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données JSON invalides.'}, status=400)

    user_to_delete = get_object_or_404(User, email=email)

    try:
        User.objects.delete_user(user_to_delete)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'success': "Utilisateur supprimé avec succès."})

@login_required
@require_POST
@csrf_exempt
def toggle_user_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            user = CustomUser.objects.get(email=email)
            user.is_active = not user.is_active
            user.save()
            return JsonResponse({'success': 'Statut mis à jour.', 'is_active': user.is_active})
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'Utilisateur non trouvé.'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return JsonResponse({'error': 'Méthode non autorisée.'})