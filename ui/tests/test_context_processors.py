from ui import context_processors


def test_feature_flags_installed(settings):
    processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']

    assert 'ui.context_processors.feature_flags' in processors


def test_feature_returns_expected_features(rf, settings):
    settings.FEATURE_UNSUBSCRIBE_VIEW_ENABLED = 1
    settings.FEATURE_NEW_HEADER_FOOTER_ENABLED = 2

    actual = context_processors.feature_flags(None)

    assert actual == {
        'features': {
            'FEATURE_UNSUBSCRIBE_VIEW_ENABLED': 1,
            'FEATURE_NEW_HEADER_FOOTER_ENABLED': 2
        }
    }


def test_analytics(rf, settings):
    settings.GOOGLE_TAG_MANAGER_ID = '123'
    settings.GOOGLE_TAG_MANAGER_ENV = '?thing=1'
    settings.UTM_COOKIE_DOMAIN = '.thing.com'

    actual = context_processors.analytics(None)

    assert actual == {
        'analytics': {
            'GOOGLE_TAG_MANAGER_ID': '123',
            'GOOGLE_TAG_MANAGER_ENV': '?thing=1',
            'UTM_COOKIE_DOMAIN': '.thing.com',
        }
    }


def test_analytics_installed(settings):
    processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']

    assert 'ui.context_processors.analytics' in processors
