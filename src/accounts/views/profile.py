from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
import json

from accounts.models import CustomUser
from activityLog.models import ActivityLog

User = get_user_model()
@login_required()
def profile(request):
    """
    Handles the profile view for the user.
    """
    if request.user.is_authenticated:

        # Seulement les 20 derniers logs d'activité de l'utilisateur
        recent_logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:20]

        # If the request method is POST, update the user's profile
        if request.method == "POST":
            user = request.user
            #user.email = request.POST.get('email') # Commented out to prevent email changes
            user.username = request.POST.get('username')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')

            #Check if the user is trying to change their username to one that already exists
            if CustomUser.objects.filter(username=user.username).exclude(id=user.id).exists():
                messages.error(request, "Ce nom d'utilisateur est déjà pris.")
                return redirect('profile')

            user.save()
            # Register the log
            ActivityLog.objects.create(
                user=user,
                action_type='USER_UPDATED',
                description=f'Profile mis à jour pour user {user.username}.',
            )
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profile')
        else :
            return render(request, 'accounts/profile.html', context={'logs': recent_logs})
    else:
        return redirect('login')  # Redirect to login if not authenticated

@login_required
def search_users(request):
    if not (request.user.is_authenticated and (request.user.is_admin() or request.user.is_super_admin())):
        return JsonResponse({'results': []}, status=403)

    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    #Exclude the current user, admin and superuser on the search results,
    users_qs = User.objects.exclude(id=request.user.id).exclude(permission__in=[2, 3]).order_by('-date_joined')
    if query:
        users_qs = users_qs.filter(Q(username__istartswith=query) | Q(email__istartswith=query))

    paginator = Paginator(users_qs, 20)
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

@csrf_exempt  # Allow CSRF exemption for this view (Ajax requests)
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
        # Register the log
        ActivityLog.objects.create(
            user=request.user,
            action_type='USER_DELETED',
            description=f'Utilisateur {user_to_delete.username} supprimé avec succès.',
        )
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

            # Register the log
            ActivityLog.objects.create(
                user=request.user,
                action_type='USER_REACTIVATED' if user.is_active else 'USER_DEACTIVATED',
                description=f"Statut de l'utilisateur {user.username} mis à {'actif' if user.is_active else 'inactif'}.",
            )
            return JsonResponse({'success': 'Statut mis à jour.', 'is_active': user.is_active})
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'Utilisateur non trouvé.'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return JsonResponse({'error': 'Méthode non autorisée.'})


@login_required
def update_password(request):
    if request.method == 'POST':
        user = request.user
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        if new_password:
            if new_password != confirm_new_password:
                return render(request, 'accounts/update_password.html', {
                    'errors': ["Les mots de passe ne correspondent pas."],
                })

            if user.check_password(new_password):
                return render(request, 'accounts/update_password.html', {
                    'errors': ["Le nouveau mot de passe ne peut pas être identique à l'ancien."],
                })

            user.set_password(new_password)
            user.save()

            # Register the log
            ActivityLog.objects.create(
                user=user,
                action_type='USER_UPDATED',
                description='Mot de passe mis à jour.',
            )
            logout(request)
            return redirect('login')  # Redirect to login after password update
    return render(request, 'accounts/update_password.html')
