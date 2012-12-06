from django import template

register = template.Library()


@register.filter
def startswith(value, arg):
    """Usage, {% if value|startswith:"arg" %}"""
    return value.startswith(arg)
