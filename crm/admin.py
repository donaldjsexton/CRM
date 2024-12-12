from __future__ import unicode_literals

import calendar
import datetime
from calendar import HTMLCalendar

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from .forms import ClientForm
from .models import Client, Event, Task, Message, Vendor, Calendar


# Constants
CALENDAR_CELL_WIDTH = 150
CALENDAR_CELL_HEIGHT = 150


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientForm
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_date', 'venue', 'status', 'client')
    list_filter = ('status', 'event_date')
    search_fields = ('name', 'venue')
    autocomplete_fields = ('client',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('description', 'event', 'due_date', 'is_completed', 'overdue')
    list_filter = ('is_completed', 'due_date')
    search_fields = ('description',)

    def overdue(self, obj):
        """Check if a task is overdue based on the current date."""
        return obj.due_date and obj.due_date < now().date()

    overdue.boolean = True
    overdue.short_description = 'Overdue'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'event', 'sent_at', 'preview_content')
    list_filter = ('sent_at',)
    search_fields = ('sender', 'content')

    def preview_content(self, obj):
        """Display a preview of the message content."""
        return obj.content[:50]

    preview_content.short_description = "Content Preview"


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'phone_number', 'address', 'website')
    search_fields = ('name',)


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ['day', 'start_time', 'end_time', 'notes']
    change_list_template = 'admin/events/change_list.html'

    def changelist_view(self, request, extra_context=None):
        """Customize the changelist view to include a calendar."""
        extra_context = extra_context or {}
        selected_date = self._get_selected_date(request)

        extra_context.update({
            'previous_month': self._get_month_url(selected_date, delta=-1),
            'next_month': self._get_month_url(selected_date, delta=1),
            'calendar': self._generate_calendar(selected_date),
        })

        return super().changelist_view(request, extra_context)

    def _get_selected_date(self, request):
        """Determine the selected month from the request."""
        after_day = request.GET.get('day__gte')
        if after_day:
            try:
                year, month, _ = map(int, after_day.split('-'))
                return datetime.date(year=year, month=month, day=1)
            except ValueError:
                pass
        return datetime.date.today()

    def _get_month_url(self, date, delta):
        """Generate the URL for the previous or next month."""
        target_month = date.replace(day=1) + datetime.timedelta(days=delta * 30)
        target_month = target_month.replace(day=1)
        return f"{reverse('admin:events_event_changelist')}?day__gte={target_month}"

    def _generate_calendar(self, date):
        """Generate an HTML calendar for the given date."""
        cal = HTMLCalendar()
        html_calendar = cal.formatmonth(date.year, date.month, withyear=True)
        return mark_safe(html_calendar.replace(
            '<td ', f'<td width="{CALENDAR_CELL_WIDTH}" height="{CALENDAR_CELL_HEIGHT}" '
        ))
