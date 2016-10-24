from directory_validators import constants

from django import template

register = template.Library()


@register.filter
def no_export_intention(form):
    if not form.is_valid() and 'export_status' in form.errors:
        label = constants.NO_EXPORT_INTENTION_ERROR_LABEL
        return label in form.errors['export_status']
    return False
