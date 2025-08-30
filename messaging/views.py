from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q, Max
from django.contrib import messages as django_messages
from .models import Conversation, Message


@login_required
def messages_list_view(request):
    """Display list of conversations for the current user"""
    conversations = Conversation.objects.filter(
        participants=request.user
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')

    # Add unread count for each conversation
    for conversation in conversations:
        conversation.unread_count = Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user).count()

        conversation.other_participant = conversation.get_other_participant(request.user)
        conversation.last_message = conversation.get_last_message()

    context = {
        'conversations': conversations,
    }
    return render(request, 'messages/messages_list.html', context)


@login_required
def conversation_detail_view(request, conversation_id):
    """Display a specific conversation"""
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )

    # Mark all messages in this conversation as read
    Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)

    messages = conversation.messages.all().select_related('sender__profile')
    other_participant = conversation.get_other_participant(request.user)

    context = {
        'conversation': conversation,
        'messages': messages,
        'other_participant': other_participant,
    }
    return render(request, 'messages/conversation_detail.html', context)


@login_required
def send_message_view(request, conversation_id):
    """Send a message in a conversation"""
    if request.method == 'POST':
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            participants=request.user
        )

        content = request.POST.get('content', '').strip()
        if content:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )

            # Update conversation timestamp
            conversation.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': {
                        'id': message.id,
                        'content': message.content,
                        'sender': message.sender.username,
                        'time': message.time_since_sent(),
                        'created_at': message.created_at.isoformat(),
                    }
                })

    return redirect('messaging:conversation_detail', conversation_id=conversation_id)


@login_required
def start_conversation_view(request, username):
    """Start a new conversation with a user"""
    other_user = get_object_or_404(User, username=username)

    if other_user == request.user:
        django_messages.error(request, "You can't start a conversation with yourself.")
        return redirect('messaging:list')

    # Check if conversation already exists
    existing_conversation = Conversation.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    if existing_conversation:
        return redirect('messaging:conversation_detail', conversation_id=existing_conversation.id)

    # Create new conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)

    return redirect('messaging:conversation_detail', conversation_id=conversation.id)
