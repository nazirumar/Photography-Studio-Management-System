from django import forms

from apps.bookings.models import Booking
from apps.packages.models import Package, ServiceCategory


class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ["name", "description", "is_active"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Category name"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-input", "rows": 2, "placeholder": "Description"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = [
            "name", "category", "description", "price", "deposit_percentage",
            "duration_hours", "outfit_changes", "edited_images",
            "prints_included", "print_sizes", "frames_included", "frame_sizes",
            "album_included", "album_specification",
            "digital_files_included", "delivery_estimate_days",
            "extra_image_price", "is_active", "is_featured",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Package name"}
            ),
            "category": forms.Select(attrs={"class": "form-input"}),
            "description": forms.Textarea(
                attrs={"class": "form-input", "rows": 3, "placeholder": "Description"}
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0.00"}
            ),
            "deposit_percentage": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "50"}
            ),
            "duration_hours": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "1"}
            ),
            "outfit_changes": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "1"}
            ),
            "edited_images": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "10"}
            ),
            "prints_included": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0"}
            ),
            "frames_included": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0"}
            ),
            "album_specification": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Album details"}
            ),
            "delivery_estimate_days": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "14"}
            ),
            "extra_image_price": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0.00"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }


class PackageSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Search packages..."}
        ),
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=ServiceCategory.objects.none(),
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All"), ("active", "Active"), ("inactive", "Inactive")],
        widget=forms.Select(attrs={"class": "form-input"}),
    )


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "client", "package", "service", "title", "event_type",
            "date", "start_time", "end_time", "location", "location_type",
            "photographer", "special_instructions", "internal_notes",
        ]
        widgets = {
            "client": forms.Select(attrs={"class": "form-input"}),
            "package": forms.Select(attrs={"class": "form-input"}),
            "service": forms.Select(attrs={"class": "form-input"}),
            "title": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Booking title"}
            ),
            "event_type": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "e.g. Wedding, Portrait"}
            ),
            "date": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "start_time": forms.TimeInput(
                attrs={"class": "form-input", "type": "time"}
            ),
            "end_time": forms.TimeInput(
                attrs={"class": "form-input", "type": "time"}
            ),
            "location": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Location"}
            ),
            "location_type": forms.Select(attrs={"class": "form-input"}),
            "photographer": forms.Select(attrs={"class": "form-input"}),
            "special_instructions": forms.Textarea(
                attrs={"class": "form-input", "rows": 3, "placeholder": "Special instructions"}
            ),
            "internal_notes": forms.Textarea(
                attrs={"class": "form-input", "rows": 3, "placeholder": "Internal notes"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        photographer = cleaned_data.get("photographer")
        location = cleaned_data.get("location")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if date and photographer:
            from apps.bookings.conflict_service import check_photographer_conflicts
            conflicts = check_photographer_conflicts(
                self.instance.studio if self.instance.pk else self.initial.get("studio"),
                photographer,
                date,
                exclude_booking=self.instance if self.instance.pk else None,
            )
            if conflicts:
                conflict_refs = ", ".join([c.reference for c in conflicts])
                raise forms.ValidationError(
                    f"Photographer is already booked on this date: {conflict_refs}"
                )

        if date and location and start_time and end_time:
            from apps.bookings.conflict_service import check_location_conflicts
            conflicts = check_location_conflicts(
                self.instance.studio if self.instance.pk else self.initial.get("studio"),
                location,
                date,
                start_time,
                end_time,
                exclude_booking=self.instance if self.instance.pk else None,
            )
            if conflicts:
                conflict_refs = ", ".join([c.reference for c in conflicts])
                raise forms.ValidationError(
                    f"Location is already booked at this time: {conflict_refs}"
                )

        return cleaned_data


class BookingSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Search bookings..."}
        ),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All Statuses")] + [(c[0], c[1]) for c in Booking.Status.choices],
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"class": "form-input", "type": "date"}
        ),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"class": "form-input", "type": "date"}
        ),
    )
