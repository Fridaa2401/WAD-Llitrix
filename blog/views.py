from django.shortcuts import render, get_object_or_404, redirect
from .models import BlogPost, Comment
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import BlogPostForm, CommentForm


# MAIN PAGE --------------------
def blog_home(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, "blog/blog.html", {"posts": posts})


# BLOG-POSTS---------------------

# blog post
@login_required
def blog_post_detail(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    comments = post.comments.all().order_by('-created_at')

    return render(request, "blog/blog_post.html", {"post": post, "comments": comments})

    

# create blog post
@login_required
def create_blog_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # assign the logged-in user as the author
            post.save()
            messages.success(request, "Your blog post has been created!")
            return redirect('blog_post', post_id=post.id)
    else:
        form = BlogPostForm()
    return render(request, 'blog/create_post.html', {'form': form})

# all posts
def all_posts(request):
    # Fetch all book clubs from the database
    posts = BlogPost.objects.all()

    # If you want to allow searching for clubs, you can implement query filtering like below
    query = request.GET.get("q", "")
    if query:
        posts = posts.filter(title__icontains=query)

    # Return the posts to the template
    return render(request, "blog/blog.html", {"posts": posts})

# edit post
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.user != post.author:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('blog_post', post_id=post.id)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('blog_post', post_id=post.id)
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})

# deltete post
@login_required
def delete_blog_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.user != post.author:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect('blog_detail', post_id=post.id)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect('blog')
    return render(request, 'blog/delete_blog.html', {'post': post})



# Comments

# add comment
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.success(request, "Comment added!")
        else:
            messages.error(request, "Something went wrong with your comment.")

    return redirect("blog_post", post_id=post.id)