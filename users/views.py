from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .forms import EditProfileForm
from core.models import FriendRequest
from .forms import RegisterForm, ContactForm
from django.contrib.auth.forms import AuthenticationForm
from clubs.models import Membership, BookClub
from django.contrib import messages
from .models import CustomUser, Notification
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, datta=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                next_url = request.GET.get("next", "home")
                return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {"form": form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request, user_id=None):
    if user_id is not None:
        profile_user = get_object_or_404(CustomUser, pk=user_id)
    else:
        profile_user = request.user  
    is_own_profile = (request.user == profile_user)

    created_clubs = BookClub.objects.filter(owner=request.user)
    unread_notifications = Notification.objects.filter(recipient=request.user, unread=True)


    #MEMBERSHIP STATUS
    approved_memberships = Membership.objects.filter(user=request.user, is_approved=True)
    pending_memberships = Membership.objects.filter(user=request.user, is_pending=True)

    #FRIENDS
    is_friend = profile_user in request.user.friends.all()
    sent_request_obj = FriendRequest.objects.filter(from_user=request.user, to_user=profile_user).first()
    received_request_obj = FriendRequest.objects.filter(from_user=profile_user, to_user=request.user).first()
    incoming_requests = FriendRequest.objects.filter(to_user=profile_user)
    friends_list = profile_user.friends.all()

    return render(request, "users/profile.html", {
        "is_own_profile": is_own_profile,
        "user": profile_user,
        "approved_memberships": approved_memberships,
        "pending_memberships": pending_memberships,
        "created_clubs": created_clubs,
        "unread_notifications": unread_notifications,

        "is_friend": is_friend,                       
        "sent_request_obj": sent_request_obj,         
        "received_request_obj": received_request_obj, 
        "incoming_requests": incoming_requests,       
        "friends": friends_list, 
    })

@login_required
def public_profile(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)

    approved_memberships = Membership.objects.filter(user=profile_user, is_approved=True)
    pending_memberships = Membership.objects.filter(user=profile_user, is_pending=True)
    created_clubs = BookClub.objects.filter(owner=profile_user)

    return render(request, "users/profile.html", {
        "user": profile_user,
        "created_clubs": created_clubs,
        "approved_memberships": approved_memberships,
        "pending_memberships": pending_memberships,
        "is_own_profile": request.user == profile_user,
    })

@login_required
def profile(request):
    # Add this to your existing context
    friend_requests = FriendRequest.objects.filter(to_user=request.user)
    
    return render(request, 'users/profile.html', {
        'created_clubs': created_clubs,
        'approved_memberships': approved_memberships,
        'pending_memberships': pending_memberships,
        'friend_requests': friend_requests,
    })

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            send_mail(
                subject,
                f"From: {name} ({email})\n\n{message}",
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "users/contact.html", {"form": form})

@login_required
def mark_notification_read(request, note_id):
    note = get_object_or_404(Notification, id=note_id, recipient=request.user)
    note.unread = False
    note.save()
    return redirect('profile')


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in if they change password
            messages.success(request, "Your profile has been updated.")
            return redirect('profile')
    else:
        form = EditProfileForm(instance=user)
    
    return render(request, 'users/edit_profile.html', {'form': form})

