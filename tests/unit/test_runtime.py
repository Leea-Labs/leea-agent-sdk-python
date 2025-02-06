import asyncio
import time

import pytest

import leea_agent_sdk.runtime as rt
from leea_agent_sdk import protocol
from leea_agent_sdk.protocol.protocol_pb2 import ServerHello, AgentHello, ExecutionRequest, ExecutionResult
from tests.unit.stubs import SummarizerAgent, DummyTransport, SummarizerAgentInput, SummarizerAgentOutput
from tests.unit.stubs import NoMessagesError


def test_handshake():
    transport: DummyTransport = DummyTransport()
    transport.to_receive.append(protocol.pack(ServerHello()))

    with pytest.raises(NoMessagesError):
        rt.start(SummarizerAgent(), transport)
    assert transport.to_receive == []
    assert len(transport.sent) == 1

    hello = protocol.unpack(transport.sent[0])
    assert isinstance(hello, AgentHello)
    assert hello.Name == SummarizerAgent().name


def test_run_agent():
    transport: DummyTransport = DummyTransport()
    transport.to_receive.append(protocol.pack(ServerHello()))
    transport.to_receive.append(protocol.pack(
        ExecutionRequest(RequestID="1", AgentID="1", Input=SummarizerAgentInput(a=1, b=1).model_dump_json())
    ))

    with pytest.raises(NoMessagesError):
        rt.start(SummarizerAgent(), transport)

    assert len(transport.sent) == 2
    output = transport.sent.pop()
    execution_result = protocol.unpack(output)
    assert isinstance(execution_result, ExecutionResult)
    assert execution_result.RequestID == "1"
    assert execution_result.IsSuccessful is True
    summarizer_output = SummarizerAgentOutput.model_validate_json(execution_result.Result)
    assert summarizer_output.value == 2


def test_parallel_running():
    transport: DummyTransport = DummyTransport()
    transport.to_receive.append(protocol.pack(ServerHello()))
    transport.to_receive.append(protocol.pack(
        ExecutionRequest(RequestID="1", AgentID="1", Input=SummarizerAgentInput(a=1, b=1, slow_motion=1).model_dump_json())
    ))
    transport.to_receive.append(protocol.pack(
        ExecutionRequest(RequestID="2", AgentID="1", Input=SummarizerAgentInput(a=1, b=1, slow_motion=1).model_dump_json())
    ))

    started_at = time.time()
    with pytest.raises(NoMessagesError):
        rt.start(SummarizerAgent(), transport)

    while len(transport.sent) < 3 and time.time() - started_at < 5:
        time.sleep(0.1)

    duration = time.time() - started_at

    assert duration <= 1.2
    assert len(transport.sent) == 3


def test_astart():
    transport: DummyTransport = DummyTransport()
    transport.to_receive.append(protocol.pack(ServerHello()))
    transport.to_receive.append(protocol.pack(
        ExecutionRequest(RequestID="1", AgentID="1", Input=SummarizerAgentInput(a=1, b=1).model_dump_json())
    ))
    with pytest.raises(NoMessagesError):
        asyncio.run(rt.astart(SummarizerAgent(), transport))

    assert len(transport.sent) == 2


def test_events():
    transport: DummyTransport = DummyTransport()
    transport.to_receive.append(protocol.pack(ServerHello()))
    transport.to_receive.append(protocol.pack(
        ExecutionRequest(RequestID="1", AgentID="1", Input=SummarizerAgentInput(a=1, b=1, create_event=True).model_dump_json())
    ))
    with pytest.raises(NoMessagesError):
        asyncio.run(rt.astart(SummarizerAgent(), transport))

    assert len(transport.sent) == 3
