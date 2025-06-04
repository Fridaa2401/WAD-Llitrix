from django.urls import path
from . import views

urlpatterns = [
    # List all public clubs (with search support)
    path("join/", views.all_clubs, name="join"),

     # Club detail page
    path("<int:club_id>/", views.club_detail, name="club_detail"),

    # Create a new club
    path("create/", views.create_club, name="create"),
    path("clubs/<int:club_id>/edit/", views.edit_club, name="edit_club"),

    # View clubs by category
    path("category/<str:category>/", views.category_clubs, name="category_clubs"),
    path("categories/", views.all_categories, name="all_categories"),

    # Request to join a club (private/public clubs)
    path("<int:club_id>/request_join/", views.request_join, name="request_join"),
    path("<int:club_id>/join/confirm/", views.join_club_confirm, name="join_club_confirm"),

    # Club Discussions
    path("<int:club_id>/discussions/", views.club_discussions, name="club_discussions"),
    path("<int:club_id>/post_message/", views.post_message, name="post_message"),

    path('clubs/<int:club_id>/rsvp/', views.rsvp_meeting, name='rsvp_meeting'),


    # Leave club
    path("<int:club_id>/leave/confirm/", views.leave_club_confirm, name="leave_club_confirm"),
    path("<int:club_id>/delete/", views.delete_club, name="delete_club"),

     # Additional membership management actions:
    path("<int:club_id>/members/", views.all_members, name="all_members"),
    path("clubs/<int:club_id>/manage_members/", views.manage_members, name="manage_members"),
    path("<int:club_id>/manage_requests/", views.manage_requests, name="manage_requests"),
    path("membership/<int:membership_id>/approve/", views.approve_membership, name="approve_membership"),
    path("membership/<int:membership_id>/reject/", views.reject_membership, name="reject_membership"),
    path("clubs/<int:club_id>/remove/<int:user_id>/", views.remove_member, name="remove_member"),
]
