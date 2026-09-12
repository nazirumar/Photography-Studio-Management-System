from django import forms

from apps.projects.models import Project, ProjectTask


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "client", "booking", "package", "photographer", "editor",
            "project_manager", "shoot_date", "expected_delivery",
            "priority", "internal_notes",
        ]
        widgets = {
            "client": forms.Select(attrs={"class": "form-input"}),
            "booking": forms.Select(attrs={"class": "form-input"}),
            "package": forms.Select(attrs={"class": "form-input"}),
            "photographer": forms.Select(attrs={"class": "form-input"}),
            "editor": forms.Select(attrs={"class": "form-input"}),
            "project_manager": forms.Select(attrs={"class": "form-input"}),
            "shoot_date": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "expected_delivery": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "priority": forms.Select(attrs={"class": "form-input"}),
            "internal_notes": forms.Textarea(
                attrs={"class": "form-input", "rows": 3, "placeholder": "Notes"}
            ),
        }


class ProjectSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Search projects..."}
        ),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All Statuses")] + [(c[0], c[1]) for c in Project.Status.choices],
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[("", "All Priorities")] + [(c[0], c[1]) for c in Project.Priority.choices],
        widget=forms.Select(attrs={"class": "form-input"}),
    )


class TaskForm(forms.ModelForm):
    class Meta:
        model = ProjectTask
        fields = ["title", "description", "assigned_to", "due_date", "priority", "notes"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Task title"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-input", "rows": 2, "placeholder": "Description"}
            ),
            "assigned_to": forms.Select(attrs={"class": "form-input"}),
            "due_date": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "priority": forms.Select(attrs={"class": "form-input"}),
            "notes": forms.Textarea(
                attrs={"class": "form-input", "rows": 2, "placeholder": "Notes"}
            ),
        }
