from datetime import datetime
from django import template
from django.utils.timesince import timesince

register = template.Library()


@register.filter("utc_timesince", is_safe=False)
def timesince_filter(value):
    """Formats a date as the time since that date (i.e. "4 days, 6 hours")."""
    if not value:
        return ''
    try:
        return timesince(value, datetime.utcnow())
    except (ValueError, TypeError):
        return ''
