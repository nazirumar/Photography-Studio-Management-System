from django import forms

from apps.leads.models import Lead


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            "name", "phone", "email", "whatsapp", "event_type",
            "expected_date", "estimated_budget", "source", "assigned_to",
            "notes", "next_follow_up", "status",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Full name"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "placeholder": "+234..."}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "email@example.com"}),
            "whatsapp": forms.TextInput(attrs={"class": "form-input", "placeholder": "+234..."}),
            "event_type": forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g. Wedding, Birthday"}),
            "expected_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "estimated_budget": forms.NumberInput(attrs={"class": "form-input", "placeholder": "0.00"}),
            "source": forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g. Instagram, Referral"}),
            "assigned_to": forms.Select(attrs={"class": "form-input"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Notes"}),
            "next_follow_up": forms.DateTimeInput(attrs={"class": "form-input", "type": "datetime-local"}),
            "status": forms.Select(attrs={"class": "form-input"}),
        }


class LeadSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Search leads...",
        }),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All Statuses")] + [(c[0], c[1]) for c in Lead.Status.choices],
        widget=forms.Select(attrs={"class": "form-input"}),
    )
