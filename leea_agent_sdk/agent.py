import json
import re
import uuid
from abc import abstractmethod, ABC
from typing import Type, Literal

import jsonschema
from pydantic import BaseModel, Field, model_validator

from leea_agent_sdk.api import LeeaApi
from leea_agent_sdk.context import ExecutionContext
from leea_agent_sdk.protocol.protocol_pb2 import ExecutionLog, ExecutionRequest, ExecutionResult
from leea_agent_sdk.transport import Transport


class RemoteAgent(BaseModel):
    id: str
    name: str
    description: str

    input_schema: dict
    output_schema: dict

    _transport: Transport = None

    def set_transport(self, transport: Transport):
        self._transport = transport

    async def call(self, context: ExecutionContext, data: any):
        jsonschema.validate(data, self.input_schema)
        request_id = str(uuid.uuid4())
        request = ExecutionRequest(
            SessionID=context.session_id,
            ParentID=context.request_id,
            RequestID=request_id,
            Input=json.dumps(data),
            AgentID=self.id
        )
        result = await self._transport.send(request, lambda msg: isinstance(msg, ExecutionResult) and msg.RequestID == request_id)
        if isinstance(result, ExecutionResult):
            if not result.IsSuccessful:
                raise RuntimeError("Call exception")  # TODO proper fix this
            result_payload = json.loads(result.Result)
            jsonschema.validate(result_payload, self.output_schema)
            return result_payload


class Agent(BaseModel, ABC):
    name: str
    display_name: str = Field(default=None)
    description: str
    avatar: bytes = Field(default=None)

    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]
    visibility: Literal["public", "private", "hidden"] = Field(default="public")

    _transport: Transport = None

    __api: LeeaApi = None

    @model_validator(mode='after')
    def _validate(self):
        if not bool(re.match(r'^[a-z]+(?:-[a-z]+)*$', self.name)):
            raise ValueError(f'name should be in kebab-case')
        if self.display_name is None or not self.display_name.strip():
            words = self.name.split('-')
            self.display_name = " ".join([words[0].capitalize()] + words[1:])
        return self

    def __get_api_client(self) -> LeeaApi:
        if self.__api is None:
            self.__api = LeeaApi()
        return self.__api

    async def get_agent(self, alias: str) -> RemoteAgent:
        agent = self.__get_api_client().get_agent(alias)
        agent['input_schema'] = json.loads(agent['input_schema'])
        agent['output_schema'] = json.loads(agent['output_schema'])
        remote_agent = RemoteAgent(**agent)
        remote_agent.set_transport(self._transport)
        return remote_agent

    def set_transport(self, transport: Transport):
        self._transport = transport

    @abstractmethod
    async def run(self, context: ExecutionContext, data: BaseModel):
        """Here goes the actual implementation of the agent."""

    async def ready(self):
        """This method is called when agent is ready to handle execution requests"""

    async def push_log(self, context: ExecutionContext, message: str):
        await self._transport.send(ExecutionLog(RequestID=context.request_id, Message=message))
