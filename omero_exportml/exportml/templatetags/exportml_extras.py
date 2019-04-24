import base64
from django import template

register = template.Library()

@register.filter(name='get_encoded')
def get_encoded(dictionary, key):
    return base64.standard_b64encode(dictionary.get(key))