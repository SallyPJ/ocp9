from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models

from PIL import Image


class Photo(models.Model):
    image = models.ImageField(blank=True, null=True)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    IMAGE_MAX_SIZE = (400, 400)
    def resize_image(self):
        image = Image.open(self.image)
        image.thumbnail(self.IMAGE_MAX_SIZE)
        image.save(self.image.path)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:  
            self.resize_image()


class Ticket(models.Model):
    photo = models.ForeignKey(Photo, null=True, on_delete=models.SET_NULL, blank=True)
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-time_created',)


class Review(models.Model):
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    headline = models.CharField(max_length=128)
    body = models.CharField(max_length=8192, blank=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-time_created']

    def star_rating(self):
        """Retourne une chaîne d'étoiles basée sur la note"""
        return "★" * self.rating + "☆" * (5 - self.rating)



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
            # ensures we don't get multiple UserFollows instances
            # for unique user-user_followed pairs
            unique_together = ('user', 'followed_user', )