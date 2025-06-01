from django.urls import path
from accounts.views.profile import (
    profile, search_users, delete_user_view,
    toggle_user_status, update_password,
    doc_admin, doc_user, faq
)
from accounts.views.auth import signup, logout_user, login_user
from accounts.views.user_detail import user_detail_view, view_403

urlpatterns = [
    path('admin/users/<str:username>/', user_detail_view, name='user_info'),
    # Auth
    path('signup/', signup, name='signup'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),

    # Password
    path('update-password/', update_password, name='update_password'),

    # Profile
    path('profile/', profile, name='profile'),

    # User management (admin only)
    path('search-users/', search_users, name='search_users'),
    path('delete-user/', delete_user_view, name='delete_user'),
    path('toggle-user-status/', toggle_user_status, name='toggle_user_status'),

    # Docs / FAQ
    path('doc-admin/', doc_admin, name='doc_admin'),
    path('doc-user/', doc_user, name='doc_user'),
    path('faq/', faq, name="faq"),

    # Error
    path('403/', view_403, name='403'),
]
