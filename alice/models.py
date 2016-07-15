class User(object):
    """
    Not a real user, but enough so that a typical Django user property test
    will pass.
    """

    def __init__(self, is_authenticated=True, **kwargs):
        """
        IMPORTANT: This code effectively allows `kwargs` to override properties
        IMPORTANT: of our fake user object.  This is intentional, as it would
        IMPORTANT: allow one to create a super user simply by issuing
        IMPORTANT: `User(is_authenticated=True, superuser=True)`.
        IMPORTANT: This shouldn't be a problem though, since kwargs is only
        IMPORTANT: ever sourced from a JWT-verified dictionary (in Alice's
        IMPORTANT: middleware), but if in future this is expanded, such a use
        IMPORTANT: case should be considered.
        """

        self._is_authenticated = is_authenticated

        self.id = None
        self.is_active = True
        self.is_staff = False
        self.is_superuser = False

        for k, v in kwargs.items():
            setattr(self, k, v)

    def is_authenticated(self):
        return self._is_authenticated

    @property
    def pk(self):
        return self.id
