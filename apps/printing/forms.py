from django import forms

from apps.printing.models import AlbumOrder, FrameOrder, PrintJob


class PrintJobForm(forms.ModelForm):
    class Meta:
        model = PrintJob
        fields = [
            "photo", "print_size", "quantity", "paper_type",
            "vendor", "internal_cost", "customer_price", "due_date", "notes",
        ]
        widgets = {
            "photo": forms.Select(attrs={"class": "form-input"}),
            "print_size": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "e.g. 5x7, 8x10"}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "1"}
            ),
            "paper_type": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Paper type"}
            ),
            "vendor": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Vendor"}
            ),
            "internal_cost": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0.00"}
            ),
            "customer_price": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0.00"}
            ),
            "due_date": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "notes": forms.Textarea(
                attrs={"class": "form-input", "rows": 2, "placeholder": "Notes"}
            ),
        }


class FrameOrderForm(forms.ModelForm):
    class Meta:
        model = FrameOrder
        fields = [
            "size", "frame_type", "orientation", "quantity",
            "supplier", "internal_cost", "customer_price", "due_date", "notes",
        ]
        widgets = {
            "size": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Frame size"}
            ),
            "frame_type": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Frame type"}
            ),
            "orientation": forms.Select(attrs={"class": "form-input"}),
            "quantity": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "1"}
            ),
            "supplier": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Supplier"}
            ),
            "internal_cost": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0.00"}
            ),
            "customer_price": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0.00"}
            ),
            "due_date": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "notes": forms.Textarea(
                attrs={"class": "form-input", "rows": 2, "placeholder": "Notes"}
            ),
        }


class AlbumOrderForm(forms.ModelForm):
    class Meta:
        model = AlbumOrder
        fields = [
            "album_type", "size", "pages", "supplier",
            "cost", "selling_price", "delivery_date", "notes",
        ]
        widgets = {
            "album_type": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Album type"}
            ),
            "size": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Size"}
            ),
            "pages": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "20"}
            ),
            "supplier": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Supplier"}
            ),
            "cost": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0.00"}
            ),
            "selling_price": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0.00"}
            ),
            "delivery_date": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "notes": forms.Textarea(
                attrs={"class": "form-input", "rows": 2, "placeholder": "Notes"}
            ),
        }
