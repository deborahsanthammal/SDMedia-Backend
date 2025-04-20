from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    path("signup/", UserSignup.as_view(), name="signup"),
    path("login/", UserLogin.as_view(), name="login", ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", UserProfileManagement.as_view(), name="user_profile")
]