from django import template
register = template.Library()

@register.filter
def getattribute(obj, attr):
    value = getattr(obj, attr, '')
    return value() if callable(value) else value
