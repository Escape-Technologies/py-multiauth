import abc

from pydantic import BaseModel, ConfigDict


class StrictBaseModel(BaseModel, abc.ABC):
    model_config = ConfigDict(extra='forbid')
