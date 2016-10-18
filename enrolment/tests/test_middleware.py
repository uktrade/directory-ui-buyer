from unittest import mock

from enrolment.constants import SESSION_KEY_REFERRER

from enrolment import helpers, middleware


@mock.patch.object(helpers, 'get_referrer_from_request', return_value='google')
def test_referrer_stored_in_session_if_known(
    mock_get_referrer_from_request, rf
):
    request = rf.get('/')
    request.session = {}
    instance = middleware.ReferrerMiddleware()

    instance.process_request(request)

    assert request.session[SESSION_KEY_REFERRER] == 'google'


@mock.patch.object(helpers, 'get_referrer_from_request', return_value=None)
def test_bail_out_on_unknown_referrrer(
    mock_get_referrer_from_request, rf
):
    request = rf.get('/')
    request.session = {}
    instance = middleware.ReferrerMiddleware()

    instance.process_request(request)

    assert SESSION_KEY_REFERRER not in request.session


@mock.patch.object(helpers, 'get_referrer_from_request', return_value=None)
def test_internal_browsing_once_not_overwrite_referrer(
    mock_get_referrer_from_request, rf
):
    request = rf.get('/')
    request.session = {SESSION_KEY_REFERRER: 'google'}
    instance = middleware.ReferrerMiddleware()

    instance.process_request(request)

    assert request.session[SESSION_KEY_REFERRER] == 'google'


@mock.patch.object(helpers, 'get_referrer_from_request', return_value=None)
def test_internal_browsing_multiple_not_overwrite_referrer(
    mock_get_referrer_from_request, rf
):
    request = rf.get('/')
    request.session = {SESSION_KEY_REFERRER: 'google'}
    instance = middleware.ReferrerMiddleware()

    instance.process_request(request)
    instance.process_request(request)

    assert request.session[SESSION_KEY_REFERRER] == 'google'
