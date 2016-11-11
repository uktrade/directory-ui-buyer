import http

from enrolment import constants


def test_feedback_redirect(client):
    response = client.get(reverse('feedback'))

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == constants.FEEDBACK_FORM_URL


def test_terms_redirect(rf):
    request = rf.get(reverse('terms'))

    response = TermsView.as_view()(request)

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == constants.TERMS_AND_CONDITIONS_URL


def test_new_exporter_redirect(rf):
    request = rf.get(reverse('terms'))

    response = NewToExportingView.as_view()(request)

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == constants.NEW_TO_EXPORTING_URL


def test_contact_redirect(rf):
    request = rf.get(reverse('contact'))

    response = ContactView.as_view()(request)

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == constants.CONTACT_US_URL
