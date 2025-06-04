from django import forms
from .models import BookReview, ReviewComment

# REVIEW-POST
class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ['title', 'book_name', 'book_author', 'content', 'review_picture' ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'book_name': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'review_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# REVIEW-COMMENTS
class ReviewCommentForm(forms.ModelForm):
    class Meta:
        model = ReviewComment
        fields = ['text']

