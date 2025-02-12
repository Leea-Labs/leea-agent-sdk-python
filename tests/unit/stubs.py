import os
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

    async def run(
            self, request_id: str, input: SummarizerAgentInput
    ) -> SummarizerAgentOutput:
        if input.slow_motion > 0:
            await asyncio.sleep(input.slow_motion)
        if input.create_event:
            await self.push_log(request_id, "Test Event")
        return SummarizerAgentOutput(value=input.a + input.b)


class NoMessagesError(Exception):
    pass


class alist(list):
    async def __aiter__(self):
        for _ in self:
            yield _


class DummyTransport(Transport):
    def __init__(self, to_receive=[]):
        os.environ["LEEA_WALLET_PATH"] = "tests/unit/fixtures/id.json"
        super().__init__("API_KEY")
        self.to_receive = to_receive
        self.sent = []
        self._connect_callbacks = []

    async def run(self):
        for func in self._connect_subscribers:
            await func(self)
        await self._reader_loop(alist([self._pack(msg) for msg in self.to_receive]))

    async def send(self, msg, wait_predicate: callable = None):
        self.sent.append(msg)
        if wait_predicate:
            for m in self.to_receive:
                if wait_predicate(m):
                    return m
