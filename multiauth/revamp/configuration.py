from pydantic import BaseModel, Field

from multiauth.revamp.engines.procedure import ProcedureConfiguration
from multiauth.revamp.store.user import User


class MultiauthConfiguration(BaseModel):
    """
    Multiauth configuration model.
    """

    procedures: list[ProcedureConfiguration] = Field(default_factory=list)
    users: list[User] = Field(default_factory=list)
