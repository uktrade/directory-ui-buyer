from django import forms


class PaddedCharField(forms.CharField):
    def __init__(self, fillchar, *args, **kwargs):
        self.fillchar = fillchar
        super().__init__(*args, **kwargs)

    def to_python(self, *args, **kwargs):
        value = super().to_python(*args, **kwargs)
        if value not in self.empty_values:
            return value.rjust(self.max_length, self.fillchar)
        return value
