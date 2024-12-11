from django.contrib import admin
from .models import Client, Event, Task, Message, Vendor
from .forms import ClientForm

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
        from django.utils.timezone import now
        return obj.due_date and obj.due_date < now().date()
    overdue.boolean = True
    overdue.short_description = 'Overdue'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'event', 'sent_at', 'preview_content')  # Replaced 'timestamp' with 'sent_at'
    list_filter = ('sent_at',)  # Replaced 'timestamp' with 'sent_at'
    search_fields = ('sender', 'content')

    def preview_content(self, obj):
        return obj.content[:50]  # Preview the first 50 characters of the message content
    preview_content.short_description = "Content Preview"

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'phone_number', 'address', 'website')
    search_fields = ('name',)
