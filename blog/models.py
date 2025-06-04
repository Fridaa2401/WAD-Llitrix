from django.db import models
from users.models import CustomUser
# Create your models here.

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    description = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    post_picture = models.ImageField(upload_to='posts/', default='default.jpg')


    def __str__(self):
        return self.title
    

class Comment(models.Model):
    post = models.ForeignKey(BlogPost, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name="blog_comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"