from django import forms

from apps.clients.models import Client

STATUS_CHOICES = [("", "All Statuses"), ("active", "Active"), ("archived", "Archived")]


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            "first_name", "last_name", "phone", "whatsapp", "email",
            "address", "city", "state", "notes", "referral_source",
            "assigned_to", "status",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "First name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Last name"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "+234..."}
            ),
            "whatsapp": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "+234..."}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-input", "placeholder": "email@example.com"}
            ),
            "address": forms.Textarea(
                attrs={"class": "form-input", "rows": 2, "placeholder": "Address"}
            ),
            "city": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "City"}
            ),
            "state": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "State"}
            ),
            "notes": forms.Textarea(
                attrs={"class": "form-input", "rows": 3, "placeholder": "Internal notes"}
            ),
            "referral_source": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "How did they find us?"}
            ),
            "assigned_to": forms.Select(attrs={"class": "form-input"}),
            "status": forms.Select(attrs={"class": "form-input"}),
        }


class ClientSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Search by name, phone, email..."}
        ),
    )
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-input"}),
    )
