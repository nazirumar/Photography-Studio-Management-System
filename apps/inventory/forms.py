from django import forms

from apps.inventory.models import InventoryItem, StockTransaction


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = [
            "sku", "name", "category", "quantity", "unit",
            "reorder_level", "cost_price", "supplier", "location",
            "is_active", "notes",
        ]
        widgets = {
            "sku": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "SKU"}
            ),
            "name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Item name"}
            ),
            "category": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Category"}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0"}
            ),
            "unit": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "pcs"}
            ),
            "reorder_level": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "10"}
            ),
            "cost_price": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0.00"}
            ),
            "supplier": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Supplier name"}
            ),
            "location": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Storage location"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "notes": forms.Textarea(
                attrs={"class": "form-input", "rows": 2, "placeholder": "Notes"}
            ),
        }


class InventorySearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Search inventory..."}
        ),
    )
    category = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Category"}
        ),
    )
    low_stock = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
    )


class StockTransactionForm(forms.Form):
    transaction_type = forms.ChoiceField(
        choices=StockTransaction.Type.choices,
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={"class": "form-input", "placeholder": "Quantity"}
        ),
    )
    reference = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Reference"}
        ),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-input", "rows": 2, "placeholder": "Notes"}
        ),
    )
