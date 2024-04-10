from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from tweets.forms import CreateTweetForm

from .models import Like, Tweet


class HomeView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "tweets/home.html"
    context_object_name = "tweets"

    def get_queryset(self):
        tweets = (
            Tweet.objects.all()
            .select_related("user")
            .annotate(
                liked=Exists(Like.objects.filter(user=self.request.user, tweet=OuterRef("id"))),
                like_count=Count("likes"),
            )
            .order_by("-created_at")
        )
        return tweets


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    form_class = CreateTweetForm
    template_name = "tweets/create.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    model = Tweet
    template_name = "tweets/detail.html"
    context_object_name = "tweet"

    def get_queryset(self):
        tweets = (
            Tweet.objects.all()
            .select_related("user")
            .annotate(
                liked=Exists(Like.objects.filter(user=self.request.user, tweet=OuterRef("id"))),
                like_count=Count("likes"),
            )
            .order_by("-created_at")
        )
        return tweets


class TweetDeleteView(UserPassesTestMixin, DeleteView):
    model = Tweet
    template_name = "tweets/delete.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def test_func(self):
        object = self.get_object()
        return object.user == self.request.user


class LikeView(View):

    def post(self, *args, **kwargs):
        tweet_pk = kwargs["pk"]
        self.tweet = get_object_or_404(Tweet, id=tweet_pk)
        is_liked = Like.objects.filter(tweet=self.tweet, user=self.request.user).exists()
        like_number = Like.objects.filter(tweet=self.tweet).count()
        if is_liked:
            return JsonResponse({"like_number": like_number})
        else:
            like = Like(tweet=self.tweet, user=self.request.user)
            like.save()
            new_like_number = like_number + 1
            return JsonResponse({"like_number": new_like_number})


class UnlikeView(View):

    def post(self, *args, **kwargs):
        tweet_pk = kwargs["pk"]
        self.tweet = get_object_or_404(Tweet, id=tweet_pk)
        like = Like.objects.filter(user=self.request.user, tweet=tweet_pk)
        like_number = Like.objects.filter(tweet=self.tweet).count()
        if like:
            like.delete()
            new_like_number = like_number - 1
            return JsonResponse({"like_number": new_like_number})
        else:
            return JsonResponse({"like_number": like_number})
