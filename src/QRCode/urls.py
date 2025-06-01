from django.urls import path
from . import views

urlpatterns = [
    path('', views.qr_code, name='qr_code'),
    path('search/', views.search_qrcodes, name='search_qrcodes'),
    path('<str:uuid>/', views.qr_code_detail, name='qr_code_detail'),
    path('<str:uuid>/delete', views.delete_qrcode, name='delete-qrcode'),
    path('<str:uuid>/reload/', views.reload_qrcode_image, name='reload-qrcode-image'),
]