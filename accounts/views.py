from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import SignupForm

# from django.shortcuts import render


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)
    def form_valid(self, form):
        # signupしたらそのままloginするように実装
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"


class UserProfileView(TemplateView):
    template_name = "accounts/profile.html"
