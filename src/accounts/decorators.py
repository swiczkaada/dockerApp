from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# Decorator to restrict access to users who are either admin or super admin.
def admin_or_superadmin_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_admin() or request.user.is_super_admin()):
            return view_func(request, *args, **kwargs)

        # Redirect to the 403 Forbidden page if the user lacks permission.
        return redirect('403')

    return _wrapped_view
