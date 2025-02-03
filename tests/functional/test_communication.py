import asyncio
import os
import threading
import time
from functools import partial
from typing import Type

import pytest

from pydantic import BaseModel, Field

from leea_agent_sdk.agent import Agent
from leea_agent_sdk.runtime import start

ping_count = threading.Event()


class Ping(BaseModel):
    ping_idx: int = Field(description="Index of ping")


class Pong(BaseModel):
    pong_idx: int = Field(description="Pong index")


class PingAgent(Agent):
    name: str = "ping"
    description: str = "This agent pings pong agent"

    input_schema: Type[BaseModel] = Pong
    output_schema: Type[BaseModel] = Ping

    async def ready(self):
        await self.run("init", Pong(pong_idx=0))

    async def run(self, request_id: str, input: Pong):
        global ping_count
        ping_idx = input.pong_idx + 1
        while True:
            await self.push_log(request_id, f"Making ping {ping_idx}")
            pong = await self.get_agent("neronmoon/pong")
            result = await pong.call({'ping_idx': ping_idx})
            await self.push_log(request_id, f"Got pong {result['pong_idx']}")
            ping_idx += 1
            ping_count.set()
            await asyncio.sleep(1)


class PongAgent(Agent):
    name: str = "pong"
    description: str = "This agent responds to ping with pong"

    input_schema: Type[BaseModel] = Ping
    output_schema: Type[BaseModel] = Pong

    async def run(self, request_id: str, input: Ping):
        await self.push_log(request_id, f"Got ping {input.ping_idx}")
        return Pong(pong_idx=input.ping_idx)


def _start_agent(agent, wallet_path):
    if agent.name == 'ping':
        time.sleep(1)
    print(f"Starting {agent.name}")
    start(agent, wallet_path=wallet_path)
    print(f"Started {agent.name}")


@pytest.mark.skip("Local only")
def test_communication():
    os.environ['LEEA_API_WS_HOST'] = 'ws://localhost:1211'
    os.environ['LEEA_API_KEY'] = 'd2601d91-0108-46e3-9bc1-ccd51bdd249b'
    threads = [
        threading.Thread(target=partial(_start_agent, PingAgent(), "tests/functional/fixtures/wallet.json"), daemon=True),
        threading.Thread(target=partial(_start_agent, PongAgent(), "tests/functional/fixtures/wallet2.json"), daemon=True)
    ]
    for p in threads:
        p.start()
    for p in threads:
        p.join(timeout=2)

    global ping_count
    assert ping_count.is_set()
