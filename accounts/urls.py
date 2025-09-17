from __future__ import annotations

from django.urls import path

from .views import login_view, logout_view, profile_view, signup_view

urlpatterns = [
    path("signup", signup_view, name="signup"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("profile", profile_view, name="profile"),
]
