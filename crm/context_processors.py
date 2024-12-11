from .models import Lead, Event, Email

def global_counts(request):
    if request.user.is_authenticated:
        return {
            'leads_count': Lead.objects.count(),
            'events_count': Event.objects.count(),
            'email_count': Email.objects.filter(is_read=False).count(),
        }
    return {}  # Return an empty dictionary if the user is not logged in
