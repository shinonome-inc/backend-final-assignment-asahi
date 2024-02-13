from django.forms import ModelForm

from tweets.models import Tweet


class CreateTweetForm(ModelForm):
    class Meta:
        model = Tweet
        fields = ("content",)
