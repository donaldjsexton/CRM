from django.contrib.messages.context_processors import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Client, Event, Task, Note, Lead, Email, Vendor
from .forms import ClientForm, EventForm, AddVendorToEventForm
from .serializers import EventSerializer
from uuid import UUID
from datetime import datetime, timedelta
import calendar
from calendar import HTMLCalendar


# Home Page (Login or Dashboard)

# Home View
def home_view(request):
    return render(request, 'crm/home.html')


# Dashboard View
@login_required
def dashboard_view(request):
    context = {
        'leads_count': Lead.objects.count(),
        'events_count': Event.objects.count(),
        'email_count': Email.objects.filter(is_read=False).count(),
    }
    return render(request, 'crm/dashboard.html', context)


# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after login
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'crm/login.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('home')


def calendar_view(request):
    # Get current date or query parameters for month/year
    today = datetime.today()
    month = request.GET.get('month', today.month)
    year = request.GET.get('year', today.year)

    month = int(month)
    year = int(year)
    current_date = datetime(year, month, 1)

    # Generate all dates to display in the calendar
    first_day_of_month = current_date
    last_day_of_month = datetime(year, month, calendar.monthrange(year, month)[1])

    # Create a range to include surrounding days for the calendar grid
    start_date = first_day_of_month - timedelta(days=first_day_of_month.weekday())  # Start from the previous Monday
    end_date = last_day_of_month + timedelta(days=6 - last_day_of_month.weekday())  # End on the next Sunday

    calendar_dates = [
        start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)
    ]

    # Query database for events in the given month
    month_events = Event.objects.filter(
        event_date__year=year,
        event_date__month=month,
    )

    # Associate events with specific calendar dates
    events_by_date = {}
    for event in month_events:
        date_key = event.event_date.strftime('%Y-%m-%d')
        if date_key not in events_by_date:
            events_by_date[date_key] = []
        events_by_date[date_key].append(event)

    # Prepare navigation links
    previous_month = current_date - timedelta(days=1)
    next_month = current_date + timedelta(days=calendar.monthrange(year, month)[1])

    # Weekdays
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Pass data to the template
    context = {
        'calendar_dates': calendar_dates,
        'current_month': current_date.strftime('%B %Y'),
        'previous_month': f"?month={previous_month.month}&year={previous_month.year}",
        'next_month': f"?month={next_month.month}&year={next_month.year}",
        'days_of_week': days_of_week,
        'events_by_date': events_by_date,  # Key: date, Value: list of events
    }

    return render(request, 'crm/calendar.html', context)



def event_list_json(request):  # New name
    events = Event.objects.all()
    data = [
        {
            "id": event.id,
            "title": event.name,
            "start": event.start.isoformat(),
            "end": event.end.isoformat(),
        }
        for event in events
    ]
    return JsonResponse(data, safe=False)


class EventListAPIView(APIView):
    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)


# Event Views
def event_list(request):
    events = Event.objects.all()
    return render(request, 'crm/event_list.html', {'events': events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    tasks = event.tasks.all()
    messages = event.messages.all()
    return render(request, 'crm/event_detail.html', {'event': event, 'tasks': tasks, 'messages': messages})


def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'crm/event_form.html', {'form': form})


def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', pk=pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'crm/event_form.html', {'form': form})


def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        event.delete()
        return redirect('event_list')
    return render(request, 'crm/event_confirm_delete.html', {'event': event})


# Vendor Assignment
def add_vendor_to_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        form = AddVendorToEventForm(request.POST)
        if form.is_valid():
            vendor = form.cleaned_data['vendor']
            event.vendors.add(vendor)
            return redirect('event_detail', pk=event.pk)
    else:
        form = AddVendorToEventForm()
    return render(request, 'crm/add_vendor_to_event.html', {'event': event, 'form': form})


def remove_vendor_from_event(request, event_pk, vendor_pk):
    event = get_object_or_404(Event, pk=event_pk)
    vendor = get_object_or_404(Vendor, pk=vendor_pk)
    if request.method == "POST":
        event.vendors.remove(vendor)
        return redirect('event_detail', pk=event.pk)
    return render(request, 'crm/remove_vendor.html', {'event': event, 'vendor': vendor})

# Leads
def lead_list(request):
    leads = Lead.objects.all()
    return render(request, 'crm/lead_list.html', {'leads': leads})


# Clients
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'crm/client_list.html', {'clients': clients})


def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'crm/client_detail.html', {'client': client})


def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'crm/client_form.html', {'form': form})


# Tasks
class TaskListView(ListView):
    model = Task
    template_name = 'crm/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        # Filter tasks based on event_id passed in URL kwargs
        event_id = self.kwargs.get('event_id')
        return Task.objects.filter(event_id=event_id)

class TaskCreateView(CreateView):
    model = Task
    template_name = 'crm/task_form.html'
    fields = ['event', 'description', 'due_date', 'is_completed']
    success_url = reverse_lazy('dashboard')


class TaskUpdateView(UpdateView):
    model = Task
    template_name = 'crm/task_form.html'
    fields = ['description', 'due_date', 'is_completed']
    success_url = reverse_lazy('dashboard')


# Notes
class NoteListView(ListView):
    model = Note
    template_name = 'crm/note_list.html'
    context_object_name = 'notes'

    def get_queryset(self):
        client_id = self.request.GET.get('client_id')
        event_id = self.request.GET.get('event_id')
        if client_id:
            return Note.objects.filter(client_id=client_id)
        elif event_id:
            return Note.objects.filter(event_id=event_id)
        return Note.objects.none()


class NoteCreateView(CreateView):
    model = Note
    template_name = 'crm/note_form.html'
    fields = ['content', 'client', 'event']
    success_url = reverse_lazy('dashboard')


# Emails
def email_list(request):
    emails = Email.objects.all()
    return render(request, 'crm/email_list.html', {'emails': emails})

# Vendor list view (add this to your views.py)
def vendor_list(request):
    vendors = Vendor.objects.all()  # Assuming Vendor is a model imported correctly
    return render(request, 'crm/vendor_list.html', {'vendors': vendors})
