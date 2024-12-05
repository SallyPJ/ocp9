from django.contrib import admin

from reviews.models import Ticket, Review
from social.models import UserFollows

admin.site.register(Ticket)
admin.site.register(Review)
admin.site.register(UserFollows)

