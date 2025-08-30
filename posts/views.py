from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Post, Comment
from .forms import PostForm, CommentForm
from social.models import Like, Follow


@login_required
def feed_view(request):
    # Get posts from users that the current user follows, plus their own posts
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(
        Q(author__in=following_users) | Q(author=request.user)
    ).select_related('author__profile').prefetch_related('likes', 'comments__author')

    # If user doesn't follow anyone, show recent posts from all users
    if not posts.exists():
        posts = Post.objects.all().select_related('author__profile').prefetch_related('likes', 'comments__author')

    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Add liked status for each post
    if request.user.is_authenticated:
        for post in page_obj:
            post.is_liked = Like.objects.filter(user=request.user, post=post).exists()

    context = {
        'page_obj': page_obj,
        'post_form': PostForm(),
    }
    return render(request, 'posts/feed.html', context)


@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Your post has been created!')
            return redirect('posts:feed')
    else:
        form = PostForm()

    return render(request, 'posts/create_post.html', {'form': form})


def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.filter(parent=None).select_related('author__profile').prefetch_related('replies__author__profile')

    # Check if user liked the post
    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(user=request.user, post=post).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('posts:detail', pk=pk)
    else:
        comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def edit_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your post has been updated!')
            return redirect('posts:detail', pk=pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Your post has been deleted!')
        return redirect('posts:feed')

    return render(request, 'posts/delete_post.html', {'post': post})


@login_required
@require_POST
def like_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        is_liked = False
    else:
        is_liked = True

    # Update the likes count
    post.likes_count = Like.objects.filter(post=post).count()
    post.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'is_liked': is_liked,
            'likes_count': post.likes_count
        })

    return redirect('posts:detail', pk=pk)


@login_required
def add_comment_view(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user

            # Check if this is a reply to another comment
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(Comment, pk=parent_id)
                comment.parent = parent_comment

            comment.save()
            messages.success(request, 'Your comment has been added!')

    return redirect('posts:detail', pk=pk)


@login_required
def delete_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post_pk = comment.post.pk

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Your comment has been deleted!')

    return redirect('posts:detail', pk=post_pk)


def explore_view(request):
    posts = Post.objects.all().select_related('author__profile').prefetch_related('likes', 'comments__author')

    # Pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Add liked status for each post
    if request.user.is_authenticated:
        for post in page_obj:
            post.is_liked = Like.objects.filter(user=request.user, post=post).exists()

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/explore.html', context)


def search_posts_view(request):
    query = request.GET.get('q', '')
    posts = []

    if query:
        posts = Post.objects.filter(
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query)
        ).select_related('author__profile').prefetch_related('likes', 'comments__author')

        # Add liked status for each post
        if request.user.is_authenticated:
            for post in posts:
                post.is_liked = Like.objects.filter(user=request.user, post=post).exists()

    context = {
        'posts': posts,
        'query': query
    }
    return render(request, 'posts/search_posts.html', context)


def reels_view(request):
    """Display reels in a TikTok/Instagram Reels style interface."""
    # Get all posts to use as reels (in a real app, you'd have a separate Reel model)
    reels = Post.objects.all().select_related('author__profile').prefetch_related('likes', 'comments__author').order_by('-created_at')

    # Add liked status for each reel
    if request.user.is_authenticated:
        for reel in reels:
            reel.is_liked = Like.objects.filter(user=request.user, post=reel).exists()

    context = {
        'reels': reels,
    }
    return render(request, 'posts/reels.html', context)
