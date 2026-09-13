from django import template
from django.forms import widgets
from django.utils.safestring import mark_safe

register = template.Library()

INPUT_CLASSES = (
    "w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 "
    "placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 "
    "focus:border-brand-500 focus:bg-white transition"
)
SELECT_CLASSES = (
    "w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 "
    "focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 "
    "focus:bg-white transition"
)
TEXTAREA_CLASSES = (
    "w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 "
    "placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 "
    "focus:border-brand-500 focus:bg-white transition resize-y min-h-[100px]"
)
CHECKBOX_CLASSES = (
    "h-4 w-4 text-brand-600 border-gray-300 rounded focus:ring-brand-500/20"
)
LABEL_CLASSES = "block text-sm font-medium text-gray-700 mb-1.5"
ERROR_CLASSES = "text-red-500 text-xs mt-1.5"
HELP_CLASSES = "text-gray-400 text-xs mt-1.5"

TEXT_INPUT_TYPES = (
    widgets.TextInput,
    widgets.NumberInput,
    widgets.EmailInput,
    widgets.PasswordInput,
    widgets.URLInput,
    widgets.DateInput,
    widgets.DateTimeInput,
    widgets.TimeInput,
    widgets.FileInput,
)


def _add_classes(widget_instance, classes):
    existing = widget_instance.attrs.get("class", "")
    widget_instance.attrs["class"] = f"{existing} {classes}".strip()
    return widget_instance


def _style_field(field, input_class=INPUT_CLASSES):
    widget = field.field.widget
    if isinstance(widget, widgets.CheckboxInput):
        _add_classes(widget, CHECKBOX_CLASSES)
    elif isinstance(widget, widgets.Select):
        _add_classes(widget, SELECT_CLASSES)
    elif isinstance(widget, widgets.Textarea):
        _add_classes(widget, TEXTAREA_CLASSES)
    elif isinstance(widget, TEXT_INPUT_TYPES):
        _add_classes(widget, input_class)
    else:
        _add_classes(widget, input_class)


@register.simple_tag
def render_field(field, label_class=LABEL_CLASSES, input_class=INPUT_CLASSES):
    _style_field(field, input_class)
    errors_html = ""
    help_html = ""
    if field.errors:
        first_error = field.errors[0]
        errors_html = f'<p class="{ERROR_CLASSES}">{first_error}</p>'
    if field.help_text:
        help_html = f'<p class="{HELP_CLASSES}">{field.help_text}</p>'
    required = ""
    if field.field.required:
        required = '<span class="text-red-500">*</span>'
    html = (
        f'<div class="space-y-1.5">'
        f'<label for="{field.id_for_label}" class="{label_class}">'
        f"{field.label} {required}</label>"
        f"{field}"
        f"{errors_html}"
        f"{help_html}"
        f"</div>"
    )
    return mark_safe(html)


@register.filter(name="add_class")
def add_class(field, css_class):
    _style_field(field, css_class)
    return field


@register.inclusion_tag("partials/form_field.html")
def form_field(field):
    _style_field(field)
    return {"field": field}


@register.filter(name="split")
def split_string(value, delimiter=","):
    """Split a string by delimiter."""
    return [s.strip() for s in str(value).split(delimiter)]


@register.filter(name="dictkey")
def dictkey(dictionary, key):
    """Get a value from a nested dictionary."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, {})
    return {}


@register.filter(name="get")
def dict_get(dictionary, key):
    """Get a value from a dictionary by key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, "")
    return ""
