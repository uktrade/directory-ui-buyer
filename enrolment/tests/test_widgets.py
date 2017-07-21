from django import forms
from enrolment import widgets


def minify_html(html):
    return html.replace('  ', '').replace('\n', '')


def test_checkbox_with_inline_label():

    class MyTestForm(forms.Form):
        field = forms.BooleanField(
            widget=widgets.CheckboxWithInlineLabel(label='the label')
        )

    form = MyTestForm()

    expected_html = """
        <div class="form-field checkbox">
            <input id="id_field" name="field" type="checkbox" />
            <label for="id_field">the label</label>
        </div>
    """

    assert minify_html(expected_html) in minify_html(str(form))


def test_mutiple_choice_checkbox_with_inline_label():

    class MyTestForm(forms.Form):
        field = forms.BooleanField(
            widget=widgets.CheckboxSelectInlineLabelMultiple(
                choices=[
                    ('1', 'one'),
                    ('2', 'two'),
                    ('3', 'three'),
                ]
            )
        )

    form = MyTestForm()

    expected_html = """
    <tr>
      <th>
        <label for="id_field_0">Field:</label>
      </th>
      <td>
        <ul id="id_field">
          <li>
            <div class="form-field checkbox">
              <input id="id_field_0" name="field" type="checkbox" value="1" />
              <label for="id_field_0">one</label>
            </div>
          </li>
          <li>
            <div class="form-field checkbox">
              <input id="id_field_1" name="field" type="checkbox" value="2" />
              <label for="id_field_1">two</label>
            </div>
          </li>
          <li>
            <div class="form-field checkbox">
              <input id="id_field_2" name="field" type="checkbox" value="3" />
              <label for="id_field_2">three</label>
            </div>
          </li>
        </ul>
      </td>
    </tr>
    """

    assert minify_html(expected_html) in minify_html(str(form))
