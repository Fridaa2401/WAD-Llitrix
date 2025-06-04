from django.shortcuts import render, get_object_or_404, redirect
from .models import BookReview, ReviewComment
from .forms import BookReviewForm, ReviewCommentForm
from users.models import Notification
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Create your views here.

def reviews_list(request):
    reviews = BookReview.objects.all().order_by('-created_at')
    form = BookReviewForm()
    comment_form = ReviewCommentForm()

    if request.method == "POST":
        form = BookReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect("reviews")
        
    if request.method == "POST" and "text" in request.POST:
        comment_form = ReviewCommentForm(request.POST)
        if comment_form.is_valid():
            review_id = request.POST.get("review_id")
            review = BookReview.objects.get(pk=review_id)
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.review = review
            comment.save()

            if review.user != request.user:
                Notification.objects.create(
                    recipient=review.user,
                    actor=request.user,
                    verb="commented on your review",
                    review=review,
                    comment=comment
                )
            return redirect("reviews")

    return render(request, "reviews/reviews.html", {
        "reviews": reviews,
        "form": form,
        "comment_form": ReviewCommentForm()
    })

@login_required
def delete_review(request, pk):
    review = get_object_or_404(BookReview, pk=pk)
    if request.user == review.user:
        review.delete()
        messages.success(request, "Review deleted.")
    else:
        messages.error(request, "You can only delete your own reviews.")
    return redirect('reviews')

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(ReviewComment, pk=pk)
    if request.user == comment.user:
        comment.delete()
        messages.success(request, "Comment deleted.")
    else:
        messages.error(request, "You can only delete your own comments.")
    return redirect('reviews')