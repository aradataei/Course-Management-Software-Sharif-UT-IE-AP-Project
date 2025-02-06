from django import template

register = template.Library()

@register.filter
def percentage(value, arg):
    try:
        return f"{(float(value) / float(arg)) * 100:.1f}"
    except (ValueError, ZeroDivisionError):
        return "0"
    

@register.filter(name='split')
def split(value, arg=','):
    return value.split(arg)