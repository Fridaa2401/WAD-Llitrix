from django.db import models
from users.models import CustomUser
from django.conf import settings

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/')
    description = models.TextField(default="No description availible")

    def __str__(self):
        return self.name

class BookClub(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    current_book = models.CharField(max_length=200, blank=True, null=True)
    current_book_picture = models.ImageField(upload_to='book_cover/', default='default.jpg')
    meeting_date = models.DateTimeField(blank=True, null=True)
    meeting_location = models.CharField(max_length=225, blank=True, null=True)
    is_private = models.BooleanField(default=False)
    members = models.ManyToManyField(CustomUser, related_name='joined_clubs', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

class Membership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    club = models.ForeignKey(BookClub, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=True)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Approved" if self.is_approved else "Pending"
        return f"{self.user.username} - {self.club.name} ({status})"

class Message(models.Model):
    club = models.ForeignKey(BookClub, related_name="messages", on_delete=models.CASCADE)
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.club.name}"
    
class ArchivedBook(models.Model):
    club = models.ForeignKey(BookClub, related_name="archived_books", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    current_book_picture = models.ImageField(upload_to='archived_clubs/', null=True, blank=True)
    archived_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (archived {self.archived_at:%Y-%m-%d})"
    
class ArchivedMessage(models.Model):
    archived_book = models.ForeignKey(ArchivedBook, related_name="archived_messages", on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} on {self.archived_book.title}"
    
class RSVP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    club = models.ForeignKey(BookClub, on_delete=models.CASCADE)
    attending = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'club')
