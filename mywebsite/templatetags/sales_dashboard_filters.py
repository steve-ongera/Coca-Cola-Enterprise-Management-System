from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Sum
import math


register = template.Library()

from django import template

register = template.Library()

@register.filter
def sum_values(value):
    """Custom sum filter for template lists"""
    try:
        return sum(value)
    except (TypeError, ValueError):
        return 0

@register.filter
def sum_values(value):
    """Custom sum filter for template lists"""
    try:
        return sum(value)
    except (TypeError, ValueError):
        return 0

@register.filter
def sum_queryset(queryset, field_name):
    """Sum a specific field in a queryset"""
    try:
        return queryset.aggregate(sum=Sum(field_name))['sum'] or 0
    except (TypeError, ValueError):
        return 0

@register.filter
def format_currency(value, decimal_places=2):
    """Format a number as currency with commas and decimal places"""
    try:
        if value is None:
            return "0.00"
        formatted = f"{float(value):,.{decimal_places}f}"
        return f"${formatted}"
    except (TypeError, ValueError):
        return "0.00"

@register.filter
def percentage(value, total):
    """Calculate percentage of value from total"""
    try:
        if total == 0:
            return "0%"
        return f"{round((float(value) / float(total)) * 100)}%"
    except (TypeError, ValueError):
        return "0%"

@register.filter
def growth_rate(current, previous):
    """Calculate growth rate between two values"""
    try:
        if previous == 0:
            return "N/A"
        growth = ((float(current) - float(previous)) / float(previous)) * 100
        return f"{growth:.1f}%"
    except (TypeError, ValueError):
        return "N/A"

@register.filter
def divide(value, divisor):
    """Divide a value by a divisor"""
    try:
        if divisor == 0:
            return 0
        return float(value) / float(divisor)
    except (TypeError, ValueError):
        return 0

@register.filter
def month_name(month_number):
    """Convert month number to month name"""
    import calendar
    try:
        return calendar.month_abbr[int(month_number)]
    except (ValueError, IndexError):
        return ""

@register.filter
def safe_division(value, divisor, default=0):
    """Safe division with default fallback"""
    try:
        return float(value) / float(divisor) if float(divisor) != 0 else default
    except (TypeError, ValueError):
        return default

@register.filter
def to_json(value):
    """Convert Python object to JSON string"""
    import json
    return json.dumps(value)

@register.filter
def map_attribute(iterable, attribute_name):
    """Map an attribute from objects in an iterable"""
    return [getattr(item, attribute_name) for item in iterable]



from django import template

register = template.Library()

@register.filter
def total_sum(value):
    try:
        return sum(value)
    except:
        return 0
