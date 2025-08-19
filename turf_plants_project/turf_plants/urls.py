from django.contrib import admin
from django.urls import path, include
from accounts.views import GoogleIDTokenLogin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('google-login/', GoogleIDTokenLogin.as_view(), name='google_id_token_login'),
    path('game_api/', include('game_api.urls')),
]