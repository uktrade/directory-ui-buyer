from django import forms
from django.core.exceptions import ImproperlyConfigured

from .helpers import rabbit, get_form_field


class ReflectiveFormMetaclass(forms.forms.DeclarativeFieldsMetaclass):

    TYPES_MAP = {
        "string": forms.CharField,
        "email": forms.EmailField,
        "choice": forms.ChoiceField,
        "integer": forms.IntegerField,
        "boolean": forms.BooleanField,
        "date": forms.DateField,
        "datetime": forms.DateTimeField
    }

    reflection_url = None

    def __new__(mcs, name, bases, attrs):

        if not mcs.reflection_url:
            raise ImproperlyConfigured("reflection_url must be defined")

        new_class = forms.forms.DeclarativeFieldsMetaclass.__new__(
            mcs, name, bases, attrs)

        fields = rabbit.get(
            mcs.reflection_url + "schema/", keep_trying=True).json()

        # Attach the schema to the class itself 'cause it's handy
        new_class._schema = fields

        for name, spec in fields.items():
            if hasattr(new_class, "Meta"):
                if hasattr(new_class.Meta, "exclude"):
                    if name in new_class.Meta.exclude:
                        continue
            mcs._generate_field(new_class, name, spec)

        return new_class

    @classmethod
    def _generate_field(mcs, new_class, name, spec):

        # Don't override what might already be set on the child class
        if name in new_class.base_fields:
            return

        form_field = get_form_field(spec)

        new_class.base_fields[name] = form_field
        new_class.declared_fields[name] = form_field
