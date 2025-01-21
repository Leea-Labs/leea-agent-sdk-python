from abc import abstractmethod, ABC
from typing import Type

from pydantic import BaseModel

from leea_agent_sdk import protocol
from leea_agent_sdk.protocol.protocol_pb2 import ExecutionLog
from leea_agent_sdk.transport import Transport


class Agent(BaseModel, ABC):
    name: str
    description: str

    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]

    _transport: Transport = None

    def set_transport(self, transport: Transport):
        self._transport = transport

    @abstractmethod
    async def run(self, request_id: str, data: BaseModel):
        """Here goes the actual implementation of the agent."""

    async def push_log(self, request_id: str, message: str):
        await self._transport.send(protocol.pack(ExecutionLog(RequestID=request_id, Message=message)))
