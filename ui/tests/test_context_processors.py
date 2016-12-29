from ui import context_processors


def test_feature_flags_installed(settings):
    processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']

    assert 'ui.context_processors.feature_flags' in processors


def test_feature_returns_expected_features(rf, settings):
    request = rf.get('/')
    actual = context_processors.feature_flags(request)

    assert actual == {
        'features': {
            'FEATURE_PUBLIC_PROFILES_ENABLED': (
                settings.FEATURE_PUBLIC_PROFILES_ENABLED
            ),
        }
    }
