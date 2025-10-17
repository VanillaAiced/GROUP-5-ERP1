from django import template

register = template.Library()

@register.filter(name='getattribute')
def getattribute(obj, attr):
    """Get attribute from object"""
    try:
        if hasattr(obj, attr):
            value = getattr(obj, attr)
            # If it's a callable (like a method), call it
            if callable(value):
                return value()
            return value
        return ''
    except Exception:
        return ''

