from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='sum_attr')
def sum_attr(queryset, attr):
    """Sum a specific attribute from a list of dictionaries"""
    try:
        return sum(item.get(attr, Decimal('0.00')) for item in queryset)
    except (ValueError, TypeError):
        return Decimal('0.00')

@register.filter(name='sum_hours')
def sum_hours(queryset):
    """Sum hours from monthly data"""
    try:
        return sum(item.get('hours', Decimal('0.00')) for item in queryset)
    except (ValueError, TypeError):
        return Decimal('0.00')

@register.filter(name='sum_hours_amount')
def sum_hours_amount(queryset):
    """Sum hours amount from monthly data"""
    try:
        total = sum(item.get('hours_amount', Decimal('0.00')) for item in queryset)
        return f"{total:.2f}"
    except (ValueError, TypeError):
        return "0.00"

@register.filter(name='sum_miles')
def sum_miles(queryset):
    """Sum miles from monthly data"""
    try:
        return sum(item.get('miles', Decimal('0.00')) for item in queryset)
    except (ValueError, TypeError):
        return Decimal('0.00')

@register.filter(name='sum_mileage_amount')
def sum_mileage_amount(queryset):
    """Sum mileage amount from monthly data"""
    try:
        total = sum(item.get('mileage_amount', Decimal('0.00')) for item in queryset)
        return f"{total:.2f}"
    except (ValueError, TypeError):
        return "0.00"

@register.filter(name='sum_total_compensation')
def sum_total_compensation(queryset):
    """Sum total compensation from monthly data"""
    try:
        total = sum(item.get('total_compensation', Decimal('0.00')) for item in queryset)
        return f"{total:.2f}"
    except (ValueError, TypeError):
        return "0.00"
