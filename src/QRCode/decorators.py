from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from QRCode.models import QRCode

# Decorator to ensure that only the owner of a QR code or an admin/super admin can access the view.
def qr_owner_or_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, uuid, *args, **kwargs):
        qrcode = get_object_or_404(QRCode, uuid=uuid)

        if qrcode.user != request.user and not (request.user.is_admin() or request.user.is_super_admin()):
            return redirect('qr_code')  # ou HttpResponseForbidden


        return view_func(request, qrcode, *args, **kwargs)

    return _wrapped_view
