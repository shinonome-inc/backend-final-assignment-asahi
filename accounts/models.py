from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField()


class FriendShip(models.Model):
    follower = models.ForeignKey(User, related_name="followings", on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower} → {self.following} ({self.created_at})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following", "created_at"],
                name="friendship_unique"
            ),
        ]
