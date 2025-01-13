import re
from typing import Union, Dict, Any

from pydantic import BaseModel, Field, model_validator, TypeAdapter


class ProtoMessage(BaseModel):
    type: str = Field()

    @model_validator(mode='before')
    def _set_type(cls, values):
        if "type" not in values:
            values["type"] = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        return values

    @classmethod
    def proto_types(cls):
        result = []
        for subclass in cls.__subclasses__():
            result.append(subclass)
            result.extend(subclass.proto_types())
        return result


class Error(ProtoMessage):
    message: str


class AgentHello(ProtoMessage):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


class ServerHello(ProtoMessage):
    pass


class SessionMessage(ProtoMessage):
    session_id: int


class RunRequest(SessionMessage):
    input: Dict[str, Any]


class RunStarted(SessionMessage):
    run_id: str


class RunFinished(SessionMessage):
    output: Dict[str, Any]


class Telemetry(ProtoMessage):
    pass


messages = TypeAdapter(Union[*ProtoMessage.proto_types()])
