from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import FriendRequest, Message
from users.models import CustomUser, Notification
from django.db.models import Q



# Core parts (nav bar items)

def home(request):
    return render(request, "core/home.html")

def about(request):
    return render(request, "core/about.html", {"MEDIA_URL": settings.MEDIA_URL})

def contact(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        message = request.POST["message"]

        subject = f"New Contact Form Submission from {name}"
        full_message = f"Sender: {name} ({email})\n\nMessage:\n{message}"


        send_mail(subject, full_message, email, ["frida@email.com"], fail_silently=False,)
        return render(request, "core/contact_sent.html")

    return render(request, "core/contact.html")


def home(request):
    return render(request, "core/home.html", {"MEDIA_URL": settings.MEDIA_URL})

# Friend Requests

@login_required
def send_friend_request(request, to_user_id):
    to_user = get_object_or_404(CustomUser, id=to_user_id)

    if to_user == request.user:
        messages.error(request, "You can’t send a friend request to yourself.")
        return redirect('profile')

    if to_user in request.user.friends.all():
        messages.info(request, f"You and {to_user.username} are already friends.")
        return redirect('profile_with_id', user_id=to_user.id)

    if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        messages.info(request, "Friend request already sent.")
        return redirect('profile_with_id', user_id=to_user.id)

    reciprocal = FriendRequest.objects.filter(from_user=to_user, to_user=request.user).first()
    if reciprocal:
        request.user.friends.add(to_user)
        to_user.friends.add(request.user)
        reciprocal.delete()
        messages.success(request, f"You and {to_user.username} are now friends!")
        return redirect('profile_with_id', user_id=to_user.id)

    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    messages.success(request, f"Friend request sent to {to_user.username}.")
    return redirect('profile_with_id', user_id=to_user.id)


@login_required
def accept_friend_request(request, fr_id):
    try:
        fr = FriendRequest.objects.get(id=fr_id, to_user=request.user)
    except FriendRequest.DoesNotExist:
        messages.error(request, "That friend request no longer exists.")
        return redirect('profile')

    from_user = fr.from_user
    to_user = fr.to_user

    from_user.friends.add(to_user)
    to_user.friends.add(from_user)

    fr.delete()

    messages.success(request, f"You are now friends with {from_user.username}!")
    return redirect('profile')


@login_required
def reject_friend_request(request, fr_id):
    fr = get_object_or_404(FriendRequest, id=fr_id, to_user=request.user)
    from_username = fr.from_user.username
    fr.delete()

    messages.info(request, f"Friend request from {from_username} rejected.")
    return redirect('profile')

@login_required
def remove_friend(request, user_id):
    friend = get_object_or_404(CustomUser, id=user_id)
    request.user.friends.remove(friend)
    friend.friends.remove(request.user)

    messages.success(request, f"You are no longer friends with {friend.username}.")
    return redirect('profile')


# Messages

@login_required
def chat_thread(request, friend_id):
    friend = get_object_or_404(CustomUser, pk=friend_id)

    # Only allow chatting if they are friends
    if friend not in request.user.friends.all():
        messages.error(request, "You can only chat with someone on your friends list.")
        return redirect("profile")

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text:
            msg = Message.objects.create(
                sender=request.user,
                receiver=friend,
                text=text
            )

            Notification.objects.create(
                recipient=friend,
                actor=request.user,
                verb=f"sent you a message",
                message=msg,
            )

            return redirect("chat_thread", friend_id=friend.id)
        else:
            messages.error(request, "Message cannot be empty.")

    convo = Message.objects.filter(
        Q(sender=request.user, receiver=friend) |
        Q(sender=friend, receiver=request.user)
    ).order_by("timestamp")
    
    return render(request, "core/chat.html", {
        "friend": friend,
        "convo": convo,
    })