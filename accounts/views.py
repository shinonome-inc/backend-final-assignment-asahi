from django.conf import settings
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, TemplateView

from accounts.models import User
from tweets.models import Tweet

from .forms import SignupForm

# from django.shortcuts import render


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = settings.LOGIN_REDIRECT_URL

    def form_valid(self, form):
        # signupしたらそのままloginするように実装
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class UserProfileView(TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self,username):
        context = super().get_context_data()
        user = get_object_or_404(User, username=username)
        context['tweets'] = Tweet.objects.filter(user=user)
        return context
