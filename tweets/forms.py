from django.contrib.auth import get_user_model
from django.forms import ModelForm

from tweets.models import Tweet

User = get_user_model()


class CreateTweetForm(ModelForm):
    class Meta:
        model = Tweet
        fields = ("content",)
