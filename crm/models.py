from django.db import models
from django.core.exceptions import ValidationError
import uuid
from django.utils.timezone import now


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
    start = models.DateTimeField()  # Start date and time
    end = models.DateTimeField()  # End date and time
    venue = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('planned', 'Planned'),
            ('booked', 'Booked'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        overlapping_events = Event.objects.filter(
            venue=self.venue,
            event_date=self.event_date
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
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('contacted', 'Contacted'),
            ('converted', 'Converted'),
            ('closed', 'Closed'),
        ],
        default='new'
    )
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
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('failed', 'Failed'),
        ],
        default='draft'
    )

    def __str__(self):
        return f"Email from {self.sender} to {self.recipient} - {self.subject}"
