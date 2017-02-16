from django import template

from company import helpers


register = template.Library()


@register.filter
def chunk_list(value, length):
    return helpers.chunk_list(value or [], length)
