from django.urls import path
from .views import scan_redirect

urlpatterns = [
    path('access/<uuid:uuid_str>/', scan_redirect, name='scan-redirect'),
]