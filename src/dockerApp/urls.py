"""
URL configuration for dockerApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.defaults import server_error

from accounts.views.profile import profile
from accounts.views.auth import signup, logout_user, login_user
from QRCode.views import qr_code, qr_code_detail, delete_qrcode, index
from analytics.views import global_stats_view
from  dockerApp import  settings
from tracking.views import scan_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('500/', server_error),

    path('', index, name='index'),
    path('signup/', signup, name='signup'),
    path('logout/', logout_user, name='logout'),
    path('login/', login_user, name='login'),
    path('profile/', profile, name='profile'),

    path('qrcode/', qr_code, name='qr_code'),
    path('qrcode/<str:uuid>/', qr_code_detail, name='qr_code_detail'),
    path('qrcode/<str:uuid>/delete', delete_qrcode, name='delete-qrcode'),

    path('access/<uuid:uuid_str>/', scan_redirect, name='scan-redirect'),

    path('global/', global_stats_view, name='global_stats'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

