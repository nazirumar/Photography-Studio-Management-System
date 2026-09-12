from django import forms

from apps.gallery.models import Gallery


class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ["name", "description", "is_selection", "is_published"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Gallery name"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-input", "rows": 2, "placeholder": "Description"}
            ),
            "is_selection": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }
