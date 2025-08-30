from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import CustomUserCreationForm, UserProfileForm, UserUpdateForm
from .models import UserProfile
from posts.models import Post
from social.models import Follow


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    posts = Post.objects.filter(author=user).order_by('-created_at')

    # Pagination
    paginator = Paginator(posts, 12)  # Show 12 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Check if current user is following this profile
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=user
        ).exists()

    context = {
        'profile_user': user,
        'profile': profile,
        'page_obj': page_obj,
        'is_following': is_following,
        'is_own_profile': request.user == user,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def follow_user_view(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    if request.user != user_to_follow:
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )

        if created:
            messages.success(request, f'You are now following {user_to_follow.username}!')
        else:
            messages.info(request, f'You are already following {user_to_follow.username}.')
    else:
        messages.error(request, 'You cannot follow yourself.')

    return redirect('accounts:profile', username=username)


@login_required
def unfollow_user_view(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)

    try:
        follow = Follow.objects.get(
            follower=request.user,
            following=user_to_unfollow
        )
        follow.delete()
        messages.success(request, f'You have unfollowed {user_to_unfollow.username}.')
    except Follow.DoesNotExist:
        messages.error(request, f'You are not following {user_to_unfollow.username}.')

    return redirect('accounts:profile', username=username)


@login_required
def followers_view(request, username):
    user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=user).select_related('follower__profile')

    paginator = Paginator(followers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile_user': user,
        'page_obj': page_obj,
        'title': 'Followers'
    }
    return render(request, 'accounts/follow_list.html', context)


@login_required
def following_view(request, username):
    user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=user).select_related('following__profile')

    paginator = Paginator(following, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile_user': user,
        'page_obj': page_obj,
        'title': 'Following'
    }
    return render(request, 'accounts/follow_list.html', context)


def search_users_view(request):
    query = request.GET.get('q', '')
    users = []

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).select_related('profile').exclude(id=request.user.id if request.user.is_authenticated else None)[:20]

        # Add following status for each user
        if request.user.is_authenticated:
            following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
            for user in users:
                user.is_following = user.id in following_ids

    context = {
        'users': users,
        'query': query
    }
    return render(request, 'accounts/search_users.html', context)
