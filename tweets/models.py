from django.db import models


class Tweet(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.content} ({self.created_at})"


class Like(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet, related_name="likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.tweet} ({self.created_at})"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "tweet"], name="like_unique"),
        ]
