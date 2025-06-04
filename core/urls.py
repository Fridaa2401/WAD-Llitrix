from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    path("send-request/<int:to_user_id>/", views.send_friend_request, name="send_friend_request"),
    path("accept-request/<int:fr_id>/", views.accept_friend_request, name="accept_friend_request"),
    path("reject-request/<int:fr_id>/", views.reject_friend_request, name="reject_friend_request"),
    path("remove-friend/<int:user_id>/", views.remove_friend, name="remove_friend"),

    path("inbox/<int:friend_id>/", views.chat_thread, name="chat_thread"),
]