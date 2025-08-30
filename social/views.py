from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender__profile', 'post', 'comment').order_by('-created_at')

    # Mark all notifications as read
    notifications.filter(is_read=False).update(is_read=True)

    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'social/notifications.html', context)


@login_required
@require_POST
def mark_notifications_read_view(request):
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('social:notifications')


@login_required
def messages_view(request):
    """Display messages/conversations for the current user"""
    # Sample conversations for demo
    sample_conversations = [
        {
            'id': 1,
            'other_participant': {
                'username': 'user1',
                'first_name': 'John',
                'last_name': 'Doe',
                'profile': {
                    'profile_picture': {'url': '/static/images/default-avatar.png'},
                    'verified': True
                }
            },
            'last_message': {
                'content': 'Hey! How are you doing today?',
                'time_since_sent': '2m',
                'sender': {'username': 'user1'}
            },
            'unread_count': 2
        },
        {
            'id': 2,
            'other_participant': {
                'username': 'user2',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'profile': {
                    'profile_picture': {'url': '/static/images/default-avatar.png'},
                    'verified': False
                }
            },
            'last_message': {
                'content': 'Thanks for sharing that amazing post!',
                'time_since_sent': '1h',
                'sender': {'username': 'user2'}
            },
            'unread_count': 0
        },
        {
            'id': 3,
            'other_participant': {
                'username': 'user3',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'profile': {
                    'profile_picture': {'url': '/static/images/default-avatar.png'},
                    'verified': False
                }
            },
            'last_message': {
                'content': 'See you at the event tomorrow!',
                'time_since_sent': '3h',
                'sender': {'username': request.user.username}
            },
            'unread_count': 0
        },
        {
            'id': 4,
            'other_participant': {
                'username': 'user4',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'profile': {
                    'profile_picture': {'url': '/static/images/default-avatar.png'},
                    'verified': True
                }
            },
            'last_message': {
                'content': 'Love your latest photos! 📸',
                'time_since_sent': '5h',
                'sender': {'username': 'user4'}
            },
            'unread_count': 1
        }
    ]

    context = {
        'conversations': sample_conversations,
    }
    return render(request, 'social/messages.html', context)


@login_required
def conversation_detail_view(request, conversation_id):
    """Display a specific conversation"""
    # Sample messages for demo
    sample_messages = [
        {
            'id': 1,
            'content': 'Hey! How are you doing?',
            'sender': {'username': 'user1', 'profile': {'profile_picture': {'url': '/static/images/default-avatar.png'}}},
            'time_since_sent': '10m',
            'created_at': '2025-08-11T21:30:00Z'
        },
        {
            'id': 2,
            'content': 'I\'m doing great! Just finished working on a new project.',
            'sender': {'username': request.user.username},
            'time_since_sent': '8m',
            'created_at': '2025-08-11T21:32:00Z'
        },
        {
            'id': 3,
            'content': 'That sounds awesome! What kind of project?',
            'sender': {'username': 'user1', 'profile': {'profile_picture': {'url': '/static/images/default-avatar.png'}}},
            'time_since_sent': '5m',
            'created_at': '2025-08-11T21:35:00Z'
        },
        {
            'id': 4,
            'content': 'It\'s a social media platform with some really cool features!',
            'sender': {'username': request.user.username},
            'time_since_sent': '2m',
            'created_at': '2025-08-11T21:38:00Z'
        }
    ]

    other_participant = {
        'username': 'user1',
        'first_name': 'John',
        'profile': {
            'profile_picture': {'url': '/static/images/default-avatar.png'}
        }
    }

    context = {
        'conversation': {'id': conversation_id},
        'messages': sample_messages,
        'other_participant': other_participant,
    }
    return render(request, 'social/conversation_detail.html', context)
