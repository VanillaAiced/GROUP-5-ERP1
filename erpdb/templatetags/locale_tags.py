from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def currency_attr(value):
    """
    Returns a data attribute for currency formatting.
    Usage: {{ order.total_amount|currency_attr }}
    """
    try:
        amount = float(value)
        return mark_safe(f'<span data-currency="{amount}">${amount:,.2f}</span>')
    except (ValueError, TypeError):
        return value

@register.filter
def date_attr(value, include_time=False):
    """
    Returns a data attribute for date formatting.
    Usage: {{ order.order_date|date_attr }}
    """
    if include_time:
        return mark_safe(f'<span data-date="{value}" data-include-time>{value}</span>')
    return mark_safe(f'<span data-date="{value}">{value}</span>')

