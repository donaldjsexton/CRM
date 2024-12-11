from django import forms
from .models import Client, Event, Vendor  # Import your models here



class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'phone_number']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Client.objects.filter(email=email).exists():
            raise forms.ValidationError("A client with this email already exists.")
        return email

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'client', 'event_date', 'start', 'end', 'venue', 'description', 'status']


class AddVendorToEventForm(forms.ModelForm):
    vendors = forms.ModelMultipleChoiceField(
        queryset=Vendor.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Event
        fields = ['vendors']