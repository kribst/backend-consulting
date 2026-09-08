from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from django.conf import settings
from .views import LoginView, LogoutView, MeView

urlpatterns = [
    path("admin/connexion", LoginView.as_view(), name="admin-login"),
    path("admin/moi", MeView.as_view(), name="admin-me"),
    path("admin/deconnexion", LogoutView.as_view(), name="admin-logout"),
    path("admin/token/refresh", TokenRefreshView.as_view(), name="admin-token-refresh"),
]

