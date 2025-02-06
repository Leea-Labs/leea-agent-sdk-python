import asyncio
from typing import Type

from pydantic import BaseModel, Field

from leea_agent_sdk.agent import Agent
from leea_agent_sdk.transport import Transport


class SummarizerAgentInput(BaseModel):
    a: int = Field(description="A")
    b: int = Field(description="B")
    slow_motion: int = Field(default=0)
    create_event: bool = Field(default=False)


class SummarizerAgentOutput(BaseModel):
    value: int = Field(description="data field")


class SummarizerAgent(Agent):
    name: str = "Test"
    description: str = "This is test agent"

    input_schema: Type[BaseModel] = SummarizerAgentInput
    output_schema: Type[BaseModel] = SummarizerAgentOutput

    async def run(self, request_id: str, input: SummarizerAgentInput) -> SummarizerAgentOutput:
        if input.slow_motion > 0:
            await asyncio.sleep(input.slow_motion)
        if input.create_event:
            await self.push_event(request_id, "Test Event")
        return SummarizerAgentOutput(value=input.a + input.b)


class NoMessagesError(Exception):
    pass


class DummyTransport(Transport):
    def __init__(self, to_receive=[]):
        self.to_receive = to_receive
        self.sent = []
        self.connected = []
        self._connect_callbacks = []

    async def _get_connection(self):
        if not self.connected:
            self.connected = True
            for cb in self._connect_callbacks:
                if asyncio.iscoroutinefunction(cb):
                    await cb()
                else:
                    cb()

    async def send(self, msg: bytes):
        await self._get_connection()
        self.sent.append(msg)

    async def receive(self) -> bytes:
        await self._get_connection()
        if len(self.to_receive) > 0:
            return self.to_receive.pop(0)
        raise NoMessagesError()
