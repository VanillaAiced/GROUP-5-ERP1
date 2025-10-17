# Template tags for erpdb app
from django import template

register = template.Library()

@register.filter
def getattr(obj, attr):
    """Get attribute from object"""
    try:
        return getattr(obj, attr, '')
    except:
        return ''

