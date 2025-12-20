from django import template

register = template.Library()

@register.filter(name='dict_key')
def dict_key(dictionary, key):
    """Access dictionary value by key in templates"""
    return dictionary.get(key, [])
