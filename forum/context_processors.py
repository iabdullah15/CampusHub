from forum.models import Notification

def base_context_processor(request):
    """
    Adds notifications and unread count to the context.
    """
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')[:10]
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    else:
        notifications = []
        unread_count = 0

    return {
        'notifications': notifications,
        'unread_count': unread_count,
    }
