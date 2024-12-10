
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model that extends Django's default AbstractUser model.

    Attributes:
        USERNAME_FIELD (str): Specifies the field used for authentication.
        follows (ManyToManyField): A many-to-many relationship allowing users
                                 to follow other users (asymmetric relationship).
    """
    USERNAME_FIELD = 'username'

    follows = models.ManyToManyField(
        'self',
        symmetrical=False,
        verbose_name='suit',
    )
