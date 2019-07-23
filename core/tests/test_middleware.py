from django.contrib.auth.models import AnonymousUser
from django.template.response import TemplateResponse

from core import middleware


def test_ga360_middleware_keys(rf, user):
    request = rf.get('/')
    request.user = user
    response = TemplateResponse(request, 'core/base.html')
    response.context_data = {}
    instance = middleware.GA360Middleware()

    instance.process_template_response(request, response)

    exp_keys = [
        'business_unit',
        'login_status',
        'page_id',
        'site_language',
        'site_subsection',
        'user_id',
    ]

    for key in exp_keys:
        assert key in response.context_data['ga360']


def test_ga360_middleware_logged_in(user, rf):
    request = rf.get('/')
    request.user = user
    response = TemplateResponse(request, 'core/base.html')
    response.context_data = {}
    instance = middleware.GA360Middleware()

    instance.process_template_response(request, response)

    assert response.context_data['ga360']['user_id']
    assert response.context_data['ga360']['login_status']


def test_ga360_middleware_not_logged_in(rf):
    request = rf.get('/')
    request.user = AnonymousUser()
    response = TemplateResponse(request, 'core/base.html')
    response.context_data = {}
    instance = middleware.GA360Middleware()

    instance.process_template_response(request, response)

    assert not response.context_data['ga360']['user_id']
    assert not response.context_data['ga360']['login_status']
