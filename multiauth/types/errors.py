"""Multiauth errors."""


class AuthenticationError(Exception):

    """Specific error class raised when the authentication fails."""


class ExpiredTokenError(Exception):

    """Specific error classed raised when the token is expired."""
