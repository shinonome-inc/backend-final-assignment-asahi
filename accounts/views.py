from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView

from accounts.models import FriendShip, User
from tweets.models import Tweet

from .forms import SignupForm


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


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, username):
        context = super().get_context_data()
        user = get_object_or_404(User, username=username)
        following_friendships = FriendShip.objects.all().filter(follower=self.request.user)
        context["following"] = [friendship.following for friendship in following_friendships]
        context["follower_number"] = FriendShip.objects.all().filter(following=self.request.user).count()
        context["user"] = user
        context["tweets"] = Tweet.objects.select_related("user").filter(user=user)
        return context

class FollowView(LoginRequiredMixin,View):

    def post(self,request,username):
        following_user = get_object_or_404(User,username=username)
        # 自分自身をフォローしようとしている場合、プロフィール画面にリダイレクト
        if request.user == following_user:
            return HttpResponseRedirect(reverse_lazy("accounts:user_profile", kwargs={"username": username}))
        # 既にフォローしているかチェック
        is_following = FriendShip.objects.filter(follower=request.user, following=following_user).exists()
        # 既にフォローしている場合、プロフィール画面にリダイレクト
        if is_following:
            return HttpResponseRedirect(reverse_lazy("accounts:user_profile", kwargs={"username": username}))
        # FriendShipの作成
        follow_instance = FriendShip(follower=request.user, following=following_user)
        follow_instance.save()

        return HttpResponseRedirect(reverse_lazy(settings.LOGIN_REDIRECT_URL))


class UnFollowView(LoginRequiredMixin,View):

    def post(self,request,username):
        unfollowing_user = get_object_or_404(User,username=username)
        follow_instance = FriendShip.objects.filter(follower=request.user, following=unfollowing_user)
        # 自分自身をフォローしようとしている場合、プロフィール画面にリダイレクト
        if request.user == unfollowing_user:
            return HttpResponseRedirect(reverse_lazy("accounts:user_profile", kwargs={"username": username}))

        # フォローしていなければリダイレクト、していればフォロー解除
        if not follow_instance:
            return HttpResponseRedirect(reverse_lazy("accounts:user_profile", kwargs={"username": username}))
        else:
            follow_instance.delete()

        return HttpResponseRedirect(reverse_lazy("accounts:user_profile", kwargs={"username": username}))


class FollowingListView(LoginRequiredMixin,ListView):
    model = FriendShip
    template_name = "accounts/followingList.html"
    context_object_name = "friendships"

    def get_queryset(self):
        return FriendShip.objects.all().filter(follower=self.request.user).select_related("following").order_by("-created_at")


class FollowerListView(LoginRequiredMixin,ListView):
    model = FriendShip
    template_name = "accounts/followerList.html"
    context_object_name = "friendships"

    def get_queryset(self):
        return FriendShip.objects.all().filter(following=self.request.user).select_related("follower").order_by("-created_at")
