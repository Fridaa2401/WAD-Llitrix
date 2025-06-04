from django.db import models
from users.models import CustomUser

# Create your models here.

class BookReview(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    book_name = models.CharField(max_length=200)
    book_author = models.CharField(max_length=100, default="Unknown")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    review_picture = models.ImageField(upload_to='reviews/', default='default.jpg')

class ReviewComment(models.Model):
    review = models.ForeignKey(BookReview, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name="review_comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)