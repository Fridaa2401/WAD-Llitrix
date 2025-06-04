from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),    
    path("logout/", views.logout_view, name="logout"),
    path("logged-out/", lambda request: views.render (request, 'users/logout.html')),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path('mark-read/<int:note_id>/', views.mark_notification_read, name='mark_notification_read'),

    path("profile/<int:user_id>/", views.profile_view, name="profile_with_id"),
    path("profile/<str:username>/", views.public_profile, name="public_profile"),
    path("profile/", views.profile_view, name="profile"),
]