from django import forms

from apps.expenses.models import Expense, ExpenseCategory


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            "category", "vendor", "description", "amount", "date",
            "payment_method", "project", "notes",
        ]
        widgets = {
            "category": forms.Select(attrs={"class": "form-input"}),
            "vendor": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Vendor name"}
            ),
            "description": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Description"}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0.00"}
            ),
            "date": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "payment_method": forms.Select(attrs={"class": "form-input"}),
            "project": forms.Select(attrs={"class": "form-input"}),
            "notes": forms.Textarea(
                attrs={"class": "form-input", "rows": 2, "placeholder": "Notes"}
            ),
        }


class ExpenseSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Search expenses..."}
        ),
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=ExpenseCategory.objects.none(),
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


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ["name", "is_active"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Category name"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }
