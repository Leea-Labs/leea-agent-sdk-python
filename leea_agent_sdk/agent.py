from abc import abstractmethod, ABC
from typing import Type

from pydantic import BaseModel

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
    async def run(self, data: BaseModel):
        """Here goes the actual implementation of the agent."""

    def push_event(self, event):
        pass
