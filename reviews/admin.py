from django.contrib import admin
from .models import BookReview, ReviewComment

# Register your models here.

admin.site.register(BookReview)
admin.site.register(ReviewComment)