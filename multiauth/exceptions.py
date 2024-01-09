class MultiAuthException(Exception):
    pass


class InvalidAuthenticationException(MultiAuthException):
    pass


class InvalidConfigurationException(MultiAuthException):
    message: str
    path: str


class MissingUserException(MultiAuthException):
    user_name: str

    def __init__(self, user_name: str) -> None:
        self.user_name = user_name

    def __str__(self) -> str:
        return f'Invalid user name. User `{self.user_name}` not registered in users list.'


class MissingProcedureException(MultiAuthException):
    procedure_name: str

    def __init__(self, procedure_name: str) -> None:
        self.procedure_name = procedure_name

    def __str__(self) -> str:
        return f'Invalid procedure name. Procedure `{self.procedure_name}` not registered in procedures list.'
