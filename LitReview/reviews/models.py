from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models
from PIL import Image


class Photo(models.Model):
    """
    Represents an image uploaded by a user.

    Fields:
        - image (ImageField): The image file uploaded by the user.
        - uploader (ForeignKey): The user who uploaded the image.
        - date_created (DateTimeField): The timestamp when the image was uploaded.

    Constants:
        - IMAGE_MAX_SIZE (tuple): Maximum size for image resizing (width, height).

    Methods:
        - resize_image(): Resizes the uploaded image to fit within IMAGE_MAX_SIZE.
        - save(): Overrides the default save method to resize the image after saving.
    """
    image = models.ImageField(blank=True, null=True)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    IMAGE_MAX_SIZE = (400, 400)

    def resize_image(self):
        """
        Resizes the uploaded image to fit within the dimensions specified in IMAGE_MAX_SIZE.

        Uses the Python Imaging Library (PIL) to resize the image while maintaining aspect ratio.
        The image is resized **in place** and saved at its original path.
        """
        image = Image.open(self.image)
        image.thumbnail(self.IMAGE_MAX_SIZE)
        image.save(self.image.path)

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to ensure the image is resized after being saved.

        Args:
            *args: Positional arguments for the parent save method.
            **kwargs: Keyword arguments for the parent save method.
        """
        super().save(*args, **kwargs)
        if self.image:
            self.resize_image()


class Ticket(models.Model):
    """
    Represents a ticket created by a user to request a review.

    Fields:
        - photo (ForeignKey): Optional photo associated with the ticket.
        - title (CharField): Title of the ticket (max 128 characters).
        - description (TextField): Description or details about the ticket.
        - user (ForeignKey): The user who created the ticket.
        - time_created (DateTimeField): Timestamp when the ticket was created.

    Meta Options:
        - ordering: Orders tickets by `time_created` in descending order (newest first).
    """
    photo = models.ForeignKey(Photo, null=True, on_delete=models.SET_NULL, blank=True)
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-time_created',)


class Review(models.Model):
    """
    Represents a review written by a user for a specific ticket.

    Fields:
        - ticket (ForeignKey): The ticket this review is associated with.
        - rating (PositiveSmallIntegerField): Rating score from 0 to 5.
        - headline (CharField): Title or headline for the review.
        - body (TextField): Detailed text content of the review (optional).
        - user (ForeignKey): The user who wrote the review.
        - time_created (DateTimeField): Timestamp when the review was created.

    Meta Options:
        - ordering: Orders reviews by `time_created` in descending order (newest first).

    Methods:
        - star_rating(): Returns a visual representation of the rating in the form of stars.
    """
    ticket = models.ForeignKey(
        to=Ticket,
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0),
                    MaxValueValidator(5)])
    headline = models.CharField(max_length=128)
    body = models.CharField(
        max_length=8192,
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-time_created']

    def star_rating(self):
        """
        Returns a visual representation of the review's rating as a string of stars.

        Example:
            If `rating = 3`, the method returns '★★★☆☆'.

        Returns:
            str: A visual representation of the rating in the form of stars (e.g., ★★★☆☆).
        """
        return "★" * self.rating + "☆" * (5 - self.rating)
