from django.urls import path
from . import views

urlpatterns = [
    path('get_player/', views.get_player),
    path('pixels/', views.get_pixels),
    path('paint/', views.paint_pixel),
    path('award_hourly_xp/', views.award_hourly_xp, name='award_hourly_xp'),
]