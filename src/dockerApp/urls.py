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
from .views import index
from store.views import index as store_index, product_detail

from  dockerApp import  settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('product/<str:slug>/', product_detail, name='product-detail'),
    path('500/', server_error),

    #path('', index, name='index'),
    path('blog/', include("blog.urls")),
    path('', store_index, name='store-index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
