from django import template

register = template.Library()

@register.filter
def total_sum(value):
    try:
        return sum(value)
    except:
        return 0
