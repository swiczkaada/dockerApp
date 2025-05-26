from django.shortcuts import render, redirect


def profile(request):
    """
    Handles the profile view for the user.
    """
    if request.method == "GET" and request.user.is_authenticated:
        # Render the profile page if the user is authenticated
        return render(request, 'accounts/profile.html')
    else:
        return redirect('login')  # Redirect to login if not authenticated