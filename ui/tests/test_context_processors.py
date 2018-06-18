from ui import context_processors


def test_feature_flags_installed(settings):
    processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']

    assert 'ui.context_processors.feature_flags' in processors


def test_feature_returns_expected_features(settings):
    settings.FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED = True

    actual = context_processors.feature_flags(None)

    assert actual == {
        'features': {
            'FEATURE_COMPANIES_HOUSE_OAUTH2_ENABLED': True,
        }
    }


def test_analytics_installed(settings):
    processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']

    assert 'directory_components.context_processors.analytics' in processors
