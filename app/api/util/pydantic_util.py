import os

from pydantic import BaseModel, BaseSettings

import api

env_file = os.path.join(
    os.path.dirname(os.path.dirname(api.__file__)),
    "config",
    "%s.env" % os.getenv("ENVIRONMENT", "local"),
)


class PydanticBaseModel(BaseModel):
    class Config:
        orm_mode = True


class PydanticBaseEnvConfig(BaseSettings):
    class Config:
        env_file = env_file
