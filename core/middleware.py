from directory_components.middleware import AbstractPrefixUrlMiddleware


class PrefixUrlMiddleware(AbstractPrefixUrlMiddleware):
    prefix = '/find-a-buyer/'
