from django.core.cache import cache
from social_platform.utils import get_user_notifications_count


def performance_context(request):
    """
    Add performance-related context to all templates.
    """
    context = {}
    
    if request.user.is_authenticated:
        # Get unread notifications count
        context['unread_notifications_count'] = get_user_notifications_count(request.user)
        
        # Add user profile data
        context['user_profile'] = request.user.profile
    
    return context


def site_context(request):
    """
    Add site-wide context variables.
    """
    return {
        'site_name': 'Social Platform',
        'site_description': 'Connect with friends and share your moments',
        'current_url': request.get_full_path(),
    }
