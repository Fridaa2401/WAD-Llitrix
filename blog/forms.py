from django import forms
from .models import BlogPost, Comment


# BLOG-POSTS
class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'description', 'post_picture']

# COMMENTS
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

