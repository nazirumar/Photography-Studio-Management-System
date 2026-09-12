from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def format_change(value):
    """Format a change value for display."""
    if value is None:
        return mark_safe('<span class="text-gray-400 italic">None</span>')
    if isinstance(value, bool):
        return mark_safe('<span class="text-emerald-600">Yes</span>' if value else '<span class="text-red-600">No</span>')
    if isinstance(value, (int, float)):
        return mark_safe(f'<span class="font-mono">{value:,.2f}</span>')
    if isinstance(value, str) and len(value) > 100:
        return mark_safe(f'<span class="text-sm">{value[:100]}...</span>')
    return mark_safe(f'<span>{value}</span>')


@register.filter
def field_name(value):
    """Convert field name to human readable."""
    return value.replace("_", " ").title()
