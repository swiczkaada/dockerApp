from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404

from QRCode.models import QRCode



# Create your views here.
'''
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    target_url = models.URLField(max_length=500)
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    qr_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
'''

def qr_code(request):

    # Check if user use the form to generate a QR code
    if request.method == 'POST':
        url = request.POST.get('target_url')
        title = request.POST.get('title')

        if url and title:
            print("Generating QR Code...")
            qr_code = QRCode.objects.create(
                user=request.user,
                title=title,
                target_url=url,
                is_active=True
            )
            qr_code.save()
        return redirect('qr_code')

    qrcodes = QRCode.objects.all()
    return render(request, 'QRCode/qrcode.html' ,context={ 'qrcodes': qrcodes} )


def qr_code_detail(request, uuid):
    qrcode = get_object_or_404(QRCode, uuid=uuid)

    # Check if user use the form to update the QR code
    if request.method == 'POST':
        url = request.POST.get('target_url')
        title = request.POST.get('title')

        if url and title:
            qrcode.target_url = url
            qrcode.title = title
            qrcode.updated_at = timezone.now()
            qrcode.save()
            return redirect('qr_code_detail', uuid=qrcode.uuid)

    return render(request, 'QRCode/detail.html', context={'qrcode': qrcode})

def delete_qrcode(request,uuid):
    qrcode = get_object_or_404(QRCode, uuid=uuid)
    if qrcode:
        qrcode.delete()
        print("QR Code deleted successfully.")

    return redirect('qr_code')
