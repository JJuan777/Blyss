import base64
from django import template

register = template.Library()

@register.filter
def b64encode(value):
    """
    Convierte datos binarios (bytes) en una cadena codificada en base64.
    """
    if value:
        return base64.b64encode(value).decode("utf-8")
    return ""
