"""Multiauth errors."""


class AuthenticationError(Exception):

    """Authentication error."""

    message = 'Your authentication failed.'


class ExpiredTokenError(Exception):

    """Token expired error."""

    message = 'Your token has expired.'


class InvalidConfigurationError(Exception):

    """Generic excpetion raised for escaperc misconfiguration."""

    errno = 2

    message: str
    path: str

    def __init__(self, message: str, path: str) -> None:
        """Create the exception."""

        super().__init__(message)

        self.message = message
        self.path = path
