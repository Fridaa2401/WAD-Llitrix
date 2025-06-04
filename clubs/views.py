import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import BookClub, Membership, Category, Message, ArchivedBook, ArchivedMessage, RSVP
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import Notification


# CATEGORIES 
# Join category
def category_clubs(request, category):
    cat_obj = get_object_or_404(Category, name__iexact=category)
    clubs = BookClub.objects.filter(category=cat_obj)
    return render(request, "clubs/category_clubs.html", {"clubs": clubs, "category": cat_obj})

# All categories
def all_categories(request):
    categories = Category.objects.all()
    return render(request, "clubs/all_categories.html", {"categories": categories})


# CLUBS JOIN
# Join club page: 
def join_club_page(request):
    clubs = BookClub.objects.all()
    print("Clubs:", clubs)  # for debugging

    categories = Category.objects.all()
    print("Categories:", categories)  # for debugging

    return render(request, "clubs/join.html", {"clubs": clubs, "categories": categories})

# Request Join
@login_required(login_url="/login/")
def request_join(request, club_id):
    club = get_object_or_404(BookClub, id=club_id)
    membership = Membership.objects.filter(user=request.user, club=club).first()

    if membership:
        if membership.is_approved:
            messages.info(request, "You are already a member of this club.")
        elif membership.is_pending:
            messages.warning(request, "You have already requested to join this club.")
        return redirect("club_detail", club_id=club.id)
    
    # For public clubs, join immediately
    if not club.is_private:
        Membership.objects.create(user=request.user, club=club, is_approved=True, is_pending=False)
        club.members.add(request.user)  # Optionally add to the many-to-many field
        messages.success(request, "You have now joined the club!")
    else:
        # For private clubs, mark as pending
        new_request = Membership.objects.create(user=request.user, club=club, is_approved=False, is_pending=True)
        messages.success(request, "Your request to join has been sent to the club owner.")
    
        Notification.objects.create(recipient=club.owner, actor=request.user, verb=f"requested to join your club \"{club.name}\"", club=club)
    
    return redirect("club_detail", club_id=club.id)

# Join Club Confirm
@login_required
def join_club_confirm(request, club_id):
    club = get_object_or_404(BookClub, id=club_id)
    # Check if the user is already in the club's members
    if request.user not in club.members.all():
        # Add the user to the club's many-to-many members field
        club.members.add(request.user)
        # Create or update the Membership record (if using the Membership model)
        membership, created = Membership.objects.get_or_create(
            user=request.user,
            club=club,
            defaults={'is_approved': True, 'is_pending': False}
        )
        # Optionally, if the record exists but wasn't approved, update it:
        if not created and (not membership.is_approved or membership.is_pending):
            membership.is_approved = True
            membership.is_pending = False
            membership.save()
    return render(request, "clubs/join_club.html", {"club": club})


# MANAGING CLUBS
# Manage Requests
@login_required(login_url="/login/")
def manage_requests(request, club_id):
    club = get_object_or_404(BookClub, id=club_id)

    if request.user != club.owner:
        messages.error(request, "You are not authorised to manage this club's requests.")
        return redirect("club_detail", club_id=club.id)
    
    pending_requests = Membership.objects.filter(club=club, is_pending=True)

    return render(request, "clubs/manage_requests.html", {"club": club, "pending_request": pending_requests})

# Create a club:
@login_required(login_url="/login/")
def create_club(request):
    categories = Category.objects.all()  

    if request.method == "POST":
        name = request.POST.get("name")
        category_id = request.POST.get("category", None)  
        description = request.POST.get("description")
        current_book = request.POST.get("current_book", "")
        current_book_picture = request.POST.get("current_book_picture")
        meeting_date_str = request.POST.get("next_meeting", None)

        if meeting_date_str:
            try:
                meeting_date = datetime.datetime.fromisoformat(meeting_date_str)
            except ValueError:
                return render(request, "clubs/create.html", {
                    "categories": categories,
                    "error": "Invalid meeting date format.",
                })
        else:
            meeting_date = None

        meeting_location = request.POST.get("meeting_location", "").strip()
        is_private = request.POST.get("privacy", "") == "private"

        if not category_id:
            return render(request, "clubs/create.html", {"categories": categories, "error": "Please select a category."})

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return render(request, "clubs/create.html", {"categories": categories, "error": "Invalid category selection."})

        # Create the book club
        club = BookClub.objects.create(
            name=name,
            description=description,
            category=category,
            current_book=current_book,
            current_book_picture=current_book_picture,
            meeting_date=meeting_date,
            meeting_location=meeting_location,
            is_private=is_private,
            owner=request.user,
        )

        club.members.add(request.user)

        Membership.objects.create(user=request.user, club=club, is_approved=True, is_pending=False)
        return redirect("club_detail", club_id=club.id)

    return render(request, "clubs/create.html", {"categories": categories})  # Pass categories to template


# Club Details
def club_detail(request, club_id):
    club = get_object_or_404(BookClub, id=club_id)
    user_rsvp = None
    membership = None

    if request.user.is_authenticated:
        user_rsvp = RSVP.objects.filter(user=request.user, club=club).first()

    if request.user.is_authenticated:
        membership = Membership.objects.filter(user=request.user, club=club).first()

    return render(request, "clubs/club_detail.html", {"club": club, "membership": membership, "user_rsvp": user_rsvp})

# Edit Club
@login_required
def edit_club(request, club_id):
    club = get_object_or_404(BookClub, id=club_id)
    
    if request.user != club.owner:
        messages.error(request, "You do not have permission to edit this club.")
        return redirect('club_detail', club_id=club.id)
    
    old_book = club.current_book
    old_picture = club.current_book_picture
    old_date = club.meeting_date
    old_location = club.meeting_location

    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category', None)
        description = request.POST.get('description', '').strip()
        new_current_book = request.POST.get('current_book', '').strip()
        new_book_picture = request.POST.get("current_book_picture")
        new_meeting_date_str = request.POST.get('meeting_date', None)
        new_meeting_location = request.POST.get('meeting_location', '').strip()
        is_private = request.POST.get('privacy', '') == 'private'

        if new_meeting_date_str:
            try:
                parsed_meeting_date = datetime.datetime.fromisoformat(new_meeting_date_str)
            except ValueError:
                return render(request, "clubs/edit_club.html", {
                    'club': club,
                    'categories': categories,
                    'error': "Invalid meeting date format.",
                })
        else:
            parsed_meeting_date = None

        category = Category.objects.get(id=category_id)

        #Save data
        club.name = name
        club.description = description
        club.category = category
        club.current_book = new_current_book or None
        club.meeting_date = parsed_meeting_date
        club.meeting_location = new_meeting_location or None
        club.is_private = is_private
        if 'current_book_picture' in request.FILES:
            club.current_book_picture = request.FILES['current_book_picture']
        club.save()

        # Archive
        if old_book and old_book != club.current_book:
            archived = ArchivedBook.objects.create(
                club=club,
                title=old_book,
                current_book_picture=old_picture
            )
            existing_msgs = Message.objects.filter(club=club).order_by("created_at")
            for msg in existing_msgs:
                ArchivedMessage.objects.create(
                    archived_book=archived,
                    user=msg.user,
                    text=msg.text,
                    created_at=msg.created_at
                )
            
            existing_msgs.delete()

        # Notifications
        if old_book != club.current_book:
            members = club.members.exclude(id=club.owner.id)  
            for member in members:
                Notification.objects.create(
                    recipient=member,
                    actor=request.user,
                    verb=f"changed the current book to '{new_current_book}' in {club.name}",
                    club=club
                )

        if old_date != club.meeting_date and club.meeting_date is not None:
            members = club.members.exclude(id=club.owner.id)
            formatted = club.meeting_date.strftime("%B %d, %Y at %I:%M %p")
            for member in members:
                Notification.objects.create(
                    recipient=member,
                    actor=request.user,
                    verb=f"scheduled a meeting on {formatted} for {club.name}",
                    club=club
                )
        
        if old_location != club.meeting_location:
            members = club.members.exclude(id=club.owner.id)  
            for member in members:
                Notification.objects.create(
                    recipient=member,
                    actor=request.user,
                    verb=f"changed the current meeting location to '{new_meeting_location}' in {club.name}",
                    club=club
                )

        messages.success(request, "Club updated successfully!")
        return redirect('club_detail', club_id=club.id)

    return render(request, 'clubs/edit_club.html', {'club': club, 'categories': categories})
   

# All Clubs
def all_clubs(request):
    clubs = BookClub.objects.all()
    query = request.GET.get("q", "")
    if query:
        clubs = clubs.filter(name__icontains=query)
    categories = Category.objects.all()
    return render(request, "clubs/join.html", {"clubs": clubs, "categories": categories})


# MEMBERS
# All members
@login_required
def all_members(request, club_id):
    club = get_object_or_404(BookClub, id=club_id)

    if request.user not in club.members.all() and request.user != club.owner:
        return redirect('club_detail', club_id=club.id)

    approved_memberships = Membership.objects.filter(
        club=club, is_approved=True
    ).select_related('user')

    return render(request, "clubs/all_members.html", {
        "club": club,
        "approved_memberships": approved_memberships,
    })


# Manage members
@login_required
def manage_members(request, club_id):
    club = get_object_or_404(BookClub, id=club_id)
    if request.user != club.owner:
        messages.error(request, "You are not authorized to manage this club.")
        return redirect("club_detail", club_id=club.id)
    
    pending_requests = Membership.objects.filter(club=club, is_pending=True)
    approved_members = Membership.objects.filter(club=club, is_approved=True)
    
    context = {
        "club": club,
        "pending_requests": pending_requests,
        "approved_members": approved_members,
    }
   
    return render(request, "clubs/manage_members.html", context)

# Approve Membership
@login_required
def approve_membership(request, membership_id):
    membership = get_object_or_404(Membership, id=membership_id)
    club = membership.club

    if request.user != club.owner:
        messages.error(request, "You are not authorized to approve memberships for this club.")
        return redirect("club_detail", club_id=club.id)

    membership.is_approved = True
    membership.is_pending = False
    membership.save()

    club.members.add(membership.user)

    messages.success(request, f"Membership for {membership.user.username} has been approved.")

    Notification.objects.create(recipient=membership.user, actor=request.user, verb=f"approved your request to join \"{club.name}\"", club=club)
    return redirect("manage_members", club_id=club.id)

# Reject Member
@login_required
def reject_membership(request, membership_id):
    membership = get_object_or_404(Membership, id=membership_id)
    club = membership.club

    # Only the club owner can reject a membership request
    if request.user != club.owner:
        messages.error(request, "You are not authorized to reject memberships for this club.")
        return redirect("club_detail", club_id=club.id)

    username = membership.user.username
    # Remove the membership record (or update its status as desired)
    membership.delete()

    messages.success(request, f"Membership for {username} has been rejected.")
    return redirect("manage_members", club_id=club.id)

# Remove Member
@login_required
def remove_member(request, club_id, user_id):
    club = get_object_or_404(BookClub, id=club_id)

    # Only the club owner can remove a member
    if request.user != club.owner:
        messages.error(request, "You are not authorized to remove members from this club.")
        return redirect("club_detail", club_id=club.id)

    # Find an approved membership for the specified user
    membership = Membership.objects.filter(club=club, user__id=user_id, is_approved=True).first()
    if membership:
        username = membership.user.username
        membership.delete()
        club.members.remove(membership.user)
        messages.success(request, f"{username} has been removed from {club.name}.")
    else:
        messages.error(request, "Member not found or not approved.")

    return redirect("manage_members", club_id=club.id)



# DISCUSSIONS
# Club discussions
def club_discussions(request, club_id):
    club = get_object_or_404(BookClub, id=club_id)
    discussions = club.messages.all().order_by("-created_at")
    upcoming_event = club.meeting_date  # adjust if you store multiple events separately
    context = {
        "club": club,
        "discussions": discussions,
        "upcoming_event": upcoming_event,
    }
    return render(request, "clubs/club_discussions.html", context)

# Post Message
@login_required
def post_message(request, club_id):
    club = get_object_or_404(BookClub, id=club_id)
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            # Create a new message linked to this club and user
            Message.objects.create(club=club, user=request.user, text=message_text)
            messages.success(request, "Your message has been posted!")
        else:
            messages.error(request, "Message cannot be empty.")
    return redirect("club_detail", club_id=club.id)


# LEAVE
# Leave Club Confirm
@login_required
def leave_club_confirm(request, club_id):
    club = get_object_or_404(BookClub, id=club_id)

    if request.user == club.owner:
        messages.error(request, "You can not leave a club you own.")
        return redirect("club_detail", club_id=club.id)

    if request.user in club.members.all():
        club.members.remove(request.user)

        Membership.objects.filter(user=request.user, club=club).delete()

    messages.success(request, f"You have left '{club.name}'.")
    return redirect('join')  # or use 'profile' or 'club_detail', etc.

# Delete Club
@login_required
def delete_club(request, club_id):
    club = get_object_or_404(BookClub, id=club_id)

    if request.user != club.owner:
        messages.error(request, "You do not have permission to delete this club.")
        return redirect('club_detail', club_id=club.id)

    if request.method == "POST":
        club.delete()
        messages.success(request, f"'{club.name}' has been deleted.")
        return redirect('join')

    return redirect('club_detail', club_id=club.id)


# RSVP
@login_required
def rsvp_meeting(request, club_id):
    club = get_object_or_404(BookClub, id=club_id)

    if request.user not in club.members.all():
        messages.error(request, "You must be a member of this club to RSVP.")
        return redirect("club_detail", club_id=club.id)
    RSVP.objects.update_or_create(user=request.user, club=club, defaults={'attending': True})

    messages.success(request, "Your RSVP has been sent.")
    return redirect('club_detail', club_id=club.id)