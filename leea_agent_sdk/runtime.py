import asyncio
import json
from threading import Thread

import leea_agent_sdk.protocol as protocol
from leea_agent_sdk.agent import Agent
from leea_agent_sdk.logger import logger
from leea_agent_sdk.protocol.protocol_pb2 import AgentHello, ServerHello, ExecutionRequest, ExecutionResult
from leea_agent_sdk.transport import Transport


def start(agent: Agent, transport: Transport = None):
    asyncio.run(astart(agent, transport))


async def astart(agent: Agent, transport: Transport = None):
    await ThreadedRuntime(agent, transport).astart()


class ThreadedRuntime:
    def __init__(self, agent: Agent, transport: Transport = None):
        self.agent = agent
        self._transport = transport or Transport()

    def start(self):
        self._aio_run(self.astart)

    async def astart(self):
        self._transport.on_connect(self._handshake)
        self.agent.set_transport(self._transport)
        while True:
            logger.info("Waiting for execution request")
            message = protocol.unpack(await self._transport.receive())
            if isinstance(message, ExecutionRequest):
                logger.info("Processing request")
                Thread(
                    target=self._aio_run,
                    args=(self._handle_execution_request, message.SerializeToString(),),
                    daemon=True
                ).start()

    def _aio_run(self, func, *args):
        asyncio.run(func(*args))

    async def _handle_execution_request(self, request_bytes: bytes):
        request = ExecutionRequest()
        request.ParseFromString(request_bytes)
        logger.info(f"Execute request {request.RequestID}")
        input_obj = self.agent.input_schema.model_validate_json(request.Input)
        result = "{}"
        try:
            success = True
            if asyncio.iscoroutinefunction(self.agent.run):
                output = await self.agent.run(request.RequestID, input_obj)
            else:
                output = self.agent.run(request.RequestID, input_obj)
            if isinstance(output, self.agent.output_schema):
                result = output.model_dump_json()
            else:
                logger.warn(f"Output is not instance of {type(self.agent.output_schema)}!")
                result = json.dumps(output)
        except Exception as e:
            logger.exception(e)
            success = False
        logger.info(f"[RequestID={request.RequestID}] {'Success' if success else 'Fail'}")
        message = ExecutionResult(RequestID=request.RequestID, Result=result, IsSuccessful=success)
        await self._transport.send(protocol.pack(message))

    async def _handshake(self):
        hello = AgentHello(
            Name=self.agent.name,
            Description=self.agent.description,
            InputSchema=json.dumps(self.agent.input_schema.model_json_schema()),
            OutputSchema=json.dumps(self.agent.output_schema.model_json_schema())
        )
        logger.info("Handshaking")
        await self._transport.send(protocol.pack(hello))
        server_hello = protocol.unpack(await self._transport.receive())
        assert isinstance(server_hello, ServerHello)
        logger.info("Handshake successful")
