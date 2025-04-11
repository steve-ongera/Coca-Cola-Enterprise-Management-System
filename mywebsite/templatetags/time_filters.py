from django import template
import datetime

register = template.Library()

@register.filter
def time_diff(check_out, check_in):
    if check_out and check_in:
        today = datetime.date.today()
        dt1 = datetime.datetime.combine(today, check_out)
        dt2 = datetime.datetime.combine(today, check_in)
        delta = dt1 - dt2
        return str(delta)
    return "-"
