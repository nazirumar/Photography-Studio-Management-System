from django import forms

from apps.equipment.models import Equipment


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            "asset_number", "name", "brand", "model_name", "serial_number",
            "purchase_date", "purchase_cost", "warranty_expiry",
            "assigned_to", "condition_notes", "maintenance_date",
            "next_maintenance", "notes",
        ]
        widgets = {
            "asset_number": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Asset #"}
            ),
            "name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Equipment name"}
            ),
            "brand": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Brand"}
            ),
            "model_name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Model"}
            ),
            "serial_number": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Serial number"}
            ),
            "purchase_date": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "purchase_cost": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0.00"}
            ),
            "warranty_expiry": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "assigned_to": forms.Select(attrs={"class": "form-input"}),
            "condition_notes": forms.Textarea(
                attrs={"class": "form-input", "rows": 2, "placeholder": "Condition notes"}
            ),
            "maintenance_date": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "next_maintenance": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "notes": forms.Textarea(
                attrs={"class": "form-input", "rows": 2, "placeholder": "Notes"}
            ),
        }


class EquipmentSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Search equipment..."}
        ),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All Statuses")] + [(c[0], c[1]) for c in Equipment.Status.choices],
        widget=forms.Select(attrs={"class": "form-input"}),
    )
