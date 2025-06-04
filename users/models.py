from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.urls import reverse




# Create your models here.

class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profiles/', default='default.jpg')
    bio = models.TextField(blank=True)

    friends = models.ManyToManyField("self", blank=True, symmetrical=True, related_name='friends_rel')

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='actor_notifications',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    verb = models.CharField(max_length=200)
    review = models.ForeignKey(
        'reviews.BookReview',
        related_name='notifications',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    comment = models.ForeignKey(
        'reviews.ReviewComment',
        related_name='notifications',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    club = models.ForeignKey(
        'clubs.BookClub',
        related_name='notifications',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    member = models.ForeignKey(
        'clubs.Membership',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    message = models.ForeignKey(
        'core.Message',
        related_name='chat_notifications',
        on_delete=models.CASCADE,
        null=True,
        blank=True
)
    timestamp = models.DateTimeField(auto_now_add=True)
    unread = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Notification(to={self.recipient}, verb='{self.verb}', unread={self.unread})"

    def get_absolute_url(self):
        if self.message:
            if self.recipient == self.message.receiver:
                other = self.message.sender
            else:
                other = self.message.receiver

            return (
                reverse('chat_thread', kwargs={'friend_id': other.id})
                + f"#msg-{self.message.id}"
            )

        if self.comment and self.review:
            return reverse('reviews') + f"#comment-{self.comment.id}"

        if self.club:
            return reverse('club_detail', kwargs={'club_id': self.club.id})

        if self.member:
            return reverse('manage_members', kwargs={'club_id': self.club.id})

        return reverse('public_profile', kwargs={'username': self.recipient.username})