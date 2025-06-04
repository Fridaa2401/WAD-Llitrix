from django.urls import path
from .views import reviews_list
from . import views

urlpatterns = [
    path("", reviews_list, name="reviews"),
    path('review/<int:pk>/delete/', views.delete_review, name='delete_review'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
]
