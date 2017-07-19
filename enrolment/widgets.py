from django.utils.safestring import mark_safe
from django.forms import widgets


class CheckboxWithInlineLabel(widgets.CheckboxInput):
    template = """
        <div class="form-field checkbox">
            {input_html}
            <label for="{id}">{label}</label>
        </div>
    """

    def __init__(self, label='', *args, **kwargs):
        self.label = label
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        input_html = super().render(name, value, attrs)
        wrapper_html = self.template.format(
            input_html=input_html, label=self.label, id=attrs['id']
        )
        return mark_safe(wrapper_html)


from django.utils.html import format_html


class CheckboxChoiceInputInlineLabel(widgets.CheckboxChoiceInput):
    template = """
        <div class="form-field checkbox">
            {input_html}
            <label for="{id}">{label}</label>
        </div>
    """

    def render(self, name=None, value=None, attrs=None, choices=()):
        if self.id_for_label:
            label_for = format_html(' for="{}"', self.id_for_label)
        else:
            label_for = ''
        attrs = dict(self.attrs, **attrs) if attrs else self.attrs
        wrapper_html = self.template.format(
            input_html=self.tag(attrs), label=self.choice_label, id=''
        )
        return mark_safe(wrapper_html)


class CheckboxFieldInlineLabelRenderer(widgets.CheckboxFieldRenderer):
    choice_input_class = CheckboxChoiceInputInlineLabel


class CheckboxSelectInlineLabelMultiple(widgets.CheckboxSelectMultiple):
    renderer = CheckboxFieldInlineLabelRenderer

