from __future__ import annotations

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


def signup_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form: UserCreationForm = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/healthz")
    else:
        form = UserCreationForm()
    return HttpResponse("ok" if form.is_bound is False else ("ok" if form.is_valid() else "bad"))


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form: AuthenticationForm = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("/healthz")
    else:
        form = AuthenticationForm(request)
    return HttpResponse("ok" if form.is_bound is False else ("ok" if form.is_valid() else "bad"))


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("/healthz")


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse(f"user:{request.user.username}")
