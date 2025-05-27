# accounts/api/urls.py
from django.urls import path
from accounts.api.views import api_signup, api_login, api_logout, api_profile

urlpatterns = [
    path('signup/', api_signup, name='api_signup'),
    path('login/', api_login, name='api_login'),
    path('logout/', api_logout, name='api_logout'),
    path('profile/', api_profile, name='api_profile'),
]
