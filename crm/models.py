from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ValidationError
import uuid
from django.utils.timezone import now

# Constants for choice fields
EVENT_STATUS_CHOICES = [
    ('planned', 'Planned'),
    ('booked', 'Booked'),
    ('completed', 'Completed'),
    ('canceled', 'Canceled'),
]

LEAD_STATUS_CHOICES = [
    ('new', 'New'),
    ('contacted', 'Contacted'),
    ('converted', 'Converted'),
    ('closed', 'Closed'),
]

EMAIL_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('sent', 'Sent'),
    ('failed', 'Failed'),
]


class Client(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Vendor(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='events')
    vendors = models.ManyToManyField(Vendor, blank=True, related_name='events')
    event_date = models.DateField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    venue = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=EVENT_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        overlapping_events = Event.objects.filter(
            venue=self.venue,
            event_date=self.event_date,
            start__lt=self.end,
            end__gt=self.start
        ).exclude(id=self.id)
        if overlapping_events.exists():
            raise ValidationError("An event is already booked at this venue on the selected date.")

    def is_upcoming(self):
        return self.event_date > now().date()

    def __str__(self):
        return self.name


class Task(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tasks')
    description = models.CharField(max_length=255)
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Task: {self.description} for {self.event.name}"


class Message(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=255)
    recipient = models.EmailField(blank=True, null=True)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient} for {self.event.name}"


class Note(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note for {self.event.name}"


class Lead(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    inquiry_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='new')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Email(models.Model):
    sender = models.EmailField()
    recipient = models.EmailField(blank=True, null=True)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=EMAIL_STATUS_CHOICES, default='draft')

    def __str__(self):
        return f"Email from {self.sender} to {self.recipient} - {self.subject}"


class Calendar(models.Model):
    day = models.DateField("Day of the Event", help_text="Day of the event")
    start_time = models.TimeField("Starting Time", help_text="Starting time")
    end_time = models.TimeField("Ending Time", help_text="Ending time")
    notes = models.TextField("Notes", blank=True, null=True)

    class Meta:
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

        overlapping_events = Calendar.objects.filter(
            day=self.day,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)

        if overlapping_events.exists():
            raise ValidationError("This event overlaps with another scheduled event.")

    def __str__(self):
        return f"Schedule on {self.day} from {self.start_time} to {self.end_time}"
