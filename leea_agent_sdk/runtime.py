import asyncio
import json
from threading import Thread

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
        self._transport.on_connected(self._handshake)
        self._transport.subscribe_message(lambda msg: isinstance(msg, ExecutionRequest), self._on_request)

        self.agent.set_transport(self._transport)
        await self._transport.run()

    def _aio_run(self, func, *args):
        asyncio.run(func(*args))

    def _on_request(self, transport: Transport, request: ExecutionRequest):
        def _handle(loop, request: ExecutionRequest):
            logger.info(f"Execute request {request.RequestID}")
            input_obj = self.agent.input_schema.model_validate_json(request.Input)
            result = "{}"
            try:
                agent_task = asyncio.run_coroutine_threadsafe(
                    self.agent.run(request.RequestID, input_obj), loop
                )
                output = agent_task.result()
                success = True
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
            asyncio.run_coroutine_threadsafe(transport.send(message), loop)

        Thread(target=_handle, args=(asyncio.get_event_loop(), request), daemon=True).start()

    async def _handshake(self, transport: Transport):
        logger.info("Handshaking")
        server_hello = await self._transport.send(AgentHello(
            Name=self.agent.name,
            Description=self.agent.description,
            InputSchema=json.dumps(self.agent.input_schema.model_json_schema()),
            OutputSchema=json.dumps(self.agent.output_schema.model_json_schema()),
            PublicKey=self._transport.get_public_key()
        ), lambda msg: isinstance(msg, ServerHello))
        assert isinstance(server_hello, ServerHello)
        logger.info("Handshake successful")
        await self.agent.ready()
