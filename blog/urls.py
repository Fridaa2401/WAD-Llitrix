from django.urls import path
from . import views  

urlpatterns = [
    path("", views.blog_home, name="blog"),
    path("create/", views.create_blog_post, name="create_post"),
    path("<int:post_id>/", views.blog_post_detail, name="blog_post"),
    path("<int:post_id>/edit/", views.edit_post, name="edit_post"),
    path("<int:post_id>/delete/", views.delete_blog_post, name="delete_blog_post"),
    path("<int:post_id>/add_comment/", views.add_comment, name="add_comment"),

]