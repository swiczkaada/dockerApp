from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Q
User = get_user_model()

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


def search_users(request):
    if not (request.user.is_authenticated and (request.user.is_admin() or request.user.is_super_admin())):
        return JsonResponse({'results': []}, status=403)

    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))

    users_qs = User.objects.exclude(id=request.user.id)
    if query:
        users_qs = users_qs.filter(Q(username__istartswith=query) | Q(email__istartswith=query))

    paginator = Paginator(users_qs, 5)
    users_page = paginator.get_page(page)

    data = [{
        'username': user.username,
        'email': user.email,
    } for user in users_page]

    return JsonResponse({
        'results': data,
        'has_next': users_page.has_next()
    })