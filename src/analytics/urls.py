from django.urls import path

from analytics.views import global_stats_view

urlpatterns = [
    path('global/', global_stats_view, name='global_stats'),
]