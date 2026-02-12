from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Session authentication that does NOT enforce CSRF.
    Intended for SPA/API usage with session cookies.
    """

    def enforce_csrf(self, request):
        return
