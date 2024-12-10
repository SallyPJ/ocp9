from django.conf import settings
from django.db import models


class UserFollows(models.Model):
    """
    Represents a 'following' relationship between users.

    This model is used to track which users are following other users.
    It also allows for blocking certain users from interacting with the current user.

    Fields:
        - user (ForeignKey): The user who is following another user.
        - followed_user (ForeignKey): The user who is being followed.
        - blocked (BooleanField): Indicates if the 'followed_user' is blocked by 'user'.

    Meta Options:
        - unique_together: Ensures that a user cannot follow the same person multiple times.

    Relationships:
        - user.following: Returns a list of users this user is following.
        - followed_user.followed_by: Returns a list of users following this user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
    )
    followed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followed_by'
    )

    blocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'followed_user', )
