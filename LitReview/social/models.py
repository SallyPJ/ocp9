from django.conf import settings
from django.db import models


class UserFollows(models.Model):
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
