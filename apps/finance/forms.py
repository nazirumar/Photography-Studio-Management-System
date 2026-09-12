from django import forms

from apps.finance.models import Invoice, Payment


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "client", "booking", "project", "issue_date", "due_date",
            "discount", "tax", "notes",
        ]
        widgets = {
            "client": forms.Select(attrs={"class": "form-input"}),
            "booking": forms.Select(attrs={"class": "form-input"}),
            "project": forms.Select(attrs={"class": "form-input"}),
            "issue_date": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "due_date": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "discount": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0.00"}
            ),
            "tax": forms.NumberInput(
                attrs={"class": "form-input", "placeholder": "0.00"}
            ),
            "notes": forms.Textarea(
                attrs={"class": "form-input", "rows": 3, "placeholder": "Notes"}
            ),
        }


class InvoiceItemForm(forms.Form):
    description = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Description"}
        ),
    )
    quantity = forms.DecimalField(
        initial=1,
        widget=forms.NumberInput(
            attrs={"class": "form-input", "placeholder": "1"}
        ),
    )
    unit_price = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={"class": "form-input", "placeholder": "0.00"}
        ),
    )


InvoiceItemFormSet = forms.formset_factory(InvoiceItemForm, extra=1)


class InvoiceSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Search invoices..."}
        ),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All Statuses")] + [(c[0], c[1]) for c in Invoice.Status.choices],
        widget=forms.Select(attrs={"class": "form-input"}),
    )


class PaymentForm(forms.Form):
    amount = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={"class": "form-input", "placeholder": "0.00"}
        ),
    )
    method = forms.ChoiceField(
        choices=Payment.Method.choices,
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    reference = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "TXN-..."}
        ),
    )
    payment_date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "form-input", "type": "date"}
        ),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-input", "rows": 2, "placeholder": "Notes"}
        ),
    )
