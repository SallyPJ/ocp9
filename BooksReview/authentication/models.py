
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    USERNAME_FIELD = 'username'

    follows = models.ManyToManyField(
        'self',
        symmetrical=False,
        verbose_name='suit',
    )










