from pydantic import BaseModel, Field

from multiauth.revamp.lib.procedure import ProcedureConfiguration
from multiauth.revamp.lib.store.user import User


class MultiauthConfiguration(BaseModel):
    """
    Multiauth configuration model.
    """

    procedures: list[ProcedureConfiguration] = Field(
        default_factory=list,
        description='The list of authentication procedures to use',
    )
    users: list[User] = Field(default_factory=list, description='List of users that can be used in procedures')
