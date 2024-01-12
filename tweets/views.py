# from django.shortcuts import render
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from tweets.forms import TweetForm

from .models import Tweet


class HomeView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "tweets/home.html"
    #作成日降順でソート
    ordering = ['-created_at']
    context_object_name = 'tweets'

    def get_queryset(self):
        return Tweet.objects.all()

class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    form_class = TweetForm
    template_name = 'tweets/create.html'
    success_url = reverse_lazy('tweets:home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TweetDetailView(LoginRequiredMixin, DetailView):
    model = Tweet
    template_name = "tweets/detail.html"
    context_object_name = "tweet"

class TweetDeleteView(LoginRequiredMixin, DeleteView):
    model = Tweet
    template_name = "tweets/delete.html"
    success_url = reverse_lazy('tweets:home')
