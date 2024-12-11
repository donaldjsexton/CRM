from django.urls import path, register_converter
from . import views
from .views import TaskListView, TaskCreateView, TaskUpdateView, NoteCreateView, NoteListView, EventListAPIView
from uuid import UUID

# Constants for common path segments
UUID_REGEX = '[0-9a-f-]{36}'
HOME_VIEW_NAME = 'home'
DASHBOARD_VIEW_NAME = 'dashboard'
CLIENT_DETAIL_VIEW_NAME = 'client_detail'
EVENT_DETAIL_VIEW_NAME = 'event_detail'


# Custom UUID converter for URL patterns
class UuidConverter:
    regex = UUID_REGEX

    def to_python(self, value):
        return UUID(value)

    def to_url(self, value):
        return str(value)


# Register the custom UUID converter
register_converter(UuidConverter, 'uuid')


# Utility function to create item detail paths
def detail_path(base_url, view_func, name_prefix):
    return [
        path(f'{base_url}/<uuid:pk>/', view_func, name=f'{name_prefix}_detail'),
        path(f'{base_url}/<uuid:pk>/edit/', view_func, name=f'{name_prefix}_edit'),
        path(f'{base_url}/<uuid:pk>/delete/', view_func, name=f'{name_prefix}_delete')
    ]


# URL patterns
urlpatterns = [
    # Home and Dashboard
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),  # Login view
    # Clients
    path('clients/', views.client_list, name='client_list'),
    path('clients/add/', views.client_create, name='client_create'),
    *detail_path('clients', views.client_detail, 'client'),

    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/add/', views.event_create, name='event_create'),
    path('events/<uuid:pk>/edit/', views.event_update, name='event_edit'),
    path('events/<uuid:pk>/add_vendor/', views.add_vendor_to_event, name='add_vendor_to_event'),
    path('events/<uuid:event_pk>/remove_vendor/<uuid:vendor_pk>/', views.remove_vendor_from_event,
         name='remove_vendor_from_event'),
    *detail_path('events/', views.event_detail, 'event'),

    # Tasks
    path('tasks/', TaskListView.as_view(), name='task_list'),  # Show a list of tasks
    path('tasks/add/', TaskCreateView.as_view(), name='task_add'),  # Add a new task
    path('tasks/<uuid:pk>/edit/', TaskUpdateView.as_view(), name='task_edit'),  # Edit an existing task

    # Notes
    path('notes/', NoteListView.as_view(), name='note_list'),
    path('notes/add/', NoteCreateView.as_view(), name='note_add'),

    # Email
    path('email/', views.email_list, name='email'),

    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/events/', views.event_list_json, name='event-list-json'),
    path('api/events/list/', EventListAPIView.as_view(), name='api_events'),

    # Leads
    path('leads/', views.lead_list, name='lead_list'),

    # Vendors
    path('vendors/', views.vendor_list, name='vendors'),

    # Authentication
    path('logout/', views.logout_view, name='logout'),
]
