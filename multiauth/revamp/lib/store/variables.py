from pydantic import BaseModel


class AuthenticationVariable(BaseModel):
    name: str
    value: str
