"""Multiauth errors."""


class AuthenticationError(Exception):

    """Specific error class raised when the authentication fails."""

    message = 'authentication error'


class ExpiredTokenError(Exception):

    """Specific error classed raised when the token is expired."""

    message = 'token is expired'


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
