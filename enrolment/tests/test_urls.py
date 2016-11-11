import http

from django.core.urlresolvers import resolve, reverse

from enrolment import constants

destinations = {
    'about': constants.ABOUT_URL,
    'contact': constants.CONTACT_US_URL,
    'events': constants.EVENTS_URL,
    'export_opportunities': constants.EXPORT_OPPORTUNITIES_URL,
    'feedback': constants.FEEDBACK_FORM_URL,
    'find_a_buyer': constants.FIND_A_BUYER_URL,
    'new_to_exporting': constants.NEW_TO_EXPORTING_URL,
    'occasional_exporter': constants.OCCASIONAL_EXPORTER_URL,
    'regular_exporter': constants.REGULAR_EXPORTER_URL,
    'selling_online_overseas': constants.SELLING_ONLINE_OVERSEAS_URL,
    'terms': constants.TERMS_AND_CONDITIONS_URL,
    'privacy': constants.PRIVACY_URL,
}


def test_redirects(rf):
    for name, expected_url in destinations.items():
        url = reverse(name)
        request = rf.get(url)
        response = resolve(url).func(request)

        assert response.status_code == http.client.FOUND
        assert response.get('Location') == expected_url
