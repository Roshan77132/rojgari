from .models import Notification


def unread_notifications(request):
    if not request.user.is_authenticated:
        return {'unread_count': 0, 'recent_notifications': []}

    qs = Notification.objects.filter(user=request.user)
    return {
        'unread_count': qs.filter(is_read=False).count(),
        'recent_notifications': list(qs[:6]),   # pachhillo 6 wota (Meta ordering -created_at)
    }