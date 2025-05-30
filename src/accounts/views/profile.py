import json


from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from QRCode.views import delete_qrcode, delete_qrcode_file
from accounts.decorators import admin_or_superadmin_required
from accounts.models import CustomUser
from activityLog.models import ActivityLog
from QRCode.models import QRCode

User = get_user_model()
@login_required()
def profile(request):
    """
    Handles the profile view for the logged-in user.
    Allows updating user info and viewing recent activity logs.
    """
    if request.user.is_authenticated:

        # Only the last 20 user activity logs
        recent_logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:20]

        # If the request method is POST, update the user's profile
        if request.method == "POST":
            user = request.user
            #user.email = request.POST.get('email') # Commented out to prevent email changes
            user.username = request.POST.get('username')
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')

            # Check if the user is trying to change their username to one that already exists
            if CustomUser.objects.filter(username=user.username).exclude(id=user.id).exists():
                messages.error(request, "Ce nom d'utilisateur est déjà pris.")
                return redirect('profile')

            user.save()
            # Log the update
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

@admin_or_superadmin_required
def search_users(request):
    """
    Search users (excluding admins, superadmins, and the current user).
    Only accessible to admin and superadmin users.
    """
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    # Exclude the current user, admin and superuser on the search results,
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
@admin_or_superadmin_required
def delete_user_view(request):
    """
    Deletes a user based on email, only accessible to admins/superadmins.
    """
    try:
        data = json.loads(request.body)
        email = data.get('email')
        if not email:
            return JsonResponse({'error': "Email manquant."}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données JSON invalides.'}, status=400)

    user_to_delete = get_object_or_404(User, email=email)

    # Delete all user QR codes with images
    qrcodes = QRCode.objects.filter(user=user_to_delete)
    for qrcode in qrcodes:
        delete_qrcode_file(qrcode)

    try:
        User.objects.delete_user(user_to_delete)
        # Log the delete
        ActivityLog.objects.create(
            user=request.user,
            action_type='USER_DELETED',
            description=f'Utilisateur {user_to_delete.username} supprimé avec succès.',
        )
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'success': "Utilisateur supprimé avec succès."})

@admin_or_superadmin_required
@require_POST
@csrf_exempt
def toggle_user_status(request):
    """
    Toggle user activation status (active/inactive).
    Only available to authorized users.
    """
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
    """
    Allows a user to update their password.
    Logs the change and logs them out after update.
    """
    if request.method == 'POST':
        user = request.user
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        if new_password:
            if new_password != confirm_new_password:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                return redirect("update_password")

            if user.check_password(new_password):
                messages.error(request, "Le nouveau mot de passe ne peut pas être identique à l'ancien.")
                return redirect("update_password")


            user.set_password(new_password)
            user.save()

            # Log the update
            ActivityLog.objects.create(
                user=user,
                action_type='USER_UPDATED',
                description='Mot de passe mis à jour.',
            )
            logout(request)
            return redirect('login')  # Redirect to login after password update
    return render(request, 'accounts/update_password.html')

@admin_or_superadmin_required
def doc_admin(request):
    """
    Renders the documentation page.
    """
    return render(request, 'accounts/doc_admin.html')

@login_required
def doc_user(request):
    """
    Renders the user documentation page.
    """
    return render(request, 'accounts/doc_user.html')

@login_required
def faq(request):
    """
    Renders the FAQ page.
    """
    faq_sections = {
        "Compte utilisateur": [
            ("Comment puis-je changer mon mot de passe ?",
             "Vous pouvez modifier votre mot de passe depuis la page « Mon compte », section « Informations personnelles ». Un lien dédié vous redirige vers la page de changement."),
            ("J'ai oublié mon mot de passe. Que faire ?",
             "Utilisez le lien « Mot de passe oublié ? » sur la page de connexion. Un e-mail vous sera envoyé pour réinitialiser votre mot de passe."),
            ("Puis-je supprimer mon compte ?",
             "La suppression définitive est possible via une demande à un administrateur. Contactez-nous via le formulaire de contact."),
        ],
        "QR Codes": [
            ("Comment créer un nouveau QR Code ?",
             "Accédez à la page « Mes QR Codes », puis cliquez sur le bouton « Créer un QR Code ». Remplissez les champs requis et validez."),
            ("Puis-je modifier un QR Code après création ?",
             "Oui, vous pouvez modifier le titre ou la redirection d’un QR Code via la page de détail."),
            ("Un QR Code supprimé est-il récupérable ?",
             "Non. La suppression est définitive. Vous pouvez toutefois le régénérer si besoin."),
        ],
        "Sécurité & Confidentialité": [
            ("Mes QR Codes sont-ils visibles par d'autres utilisateurs ?",
             "Non, chaque QR Code est privé et visible uniquement par son créateur, sauf si partagé manuellement."),
            ("Comment mes données sont-elles protégées ?",
             "Toutes les données sont stockées de manière sécurisée. Nous utilisons HTTPS, chiffrement des mots de passe et journalisation des accès."),
            ("Puis-je désactiver temporairement un QR Code ?",
             "Oui, vous pouvez désactiver un QR Code depuis la page de détail. Il ne sera alors plus fonctionnel."),
        ]
    }
    return render(request, 'accounts/faq.html', context={'faq_sections': faq_sections})


