from api.util.pydantic_util import PydanticBaseEnvConfig


class AppConfig(PydanticBaseEnvConfig):
    environment: str
