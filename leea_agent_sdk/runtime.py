import asyncio
import json
import os
from threading import Thread

from leea_agent_sdk.agent import Agent
from leea_agent_sdk.context import ExecutionContext
from leea_agent_sdk.logger import logger
from leea_agent_sdk.protocol.protocol_pb2 import AgentHello, ServerHello, ExecutionRequest, ExecutionResult
from leea_agent_sdk.transport import Transport
from leea_agent_sdk.web3_solana import Web3InstanceSolana


def start(agent: Agent, transport: Transport = None, wallet_path=None):
    asyncio.run(astart(agent, transport, wallet_path))


async def astart(agent: Agent, transport: Transport = None, wallet_path=None):
    await ThreadedRuntime(agent, transport, wallet_path).astart()


class ThreadedRuntime:
    def __init__(self, agent: Agent, transport: Transport = None, wallet_path=None):
        self.agent = agent
        self._transport = transport or Transport()
        wallet_path = wallet_path or os.getenv("LEEA_WALLET_PATH")
        self._wallet = Web3InstanceSolana(
            wallet_path if os.path.isabs(wallet_path) else os.path.join(os.getcwd(), wallet_path)
        )

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
                context = ExecutionContext(session_id=request.SessionID, request_id=request.RequestID, parent_id=request.ParentID)
                agent_task = asyncio.run_coroutine_threadsafe(
                    self.agent.run(context, input_obj), loop
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
            DisplayName=self.agent.display_name,
            Avatar=self.agent.avatar,
            Description=self.agent.description,
            InputSchema=json.dumps(self.agent.input_schema.model_json_schema()),
            OutputSchema=json.dumps(self.agent.output_schema.model_json_schema()),
            Signature=self._wallet.sign_message(self.agent.name.encode()),
            PublicKey=self._wallet.get_public_key(),
            Visibility=AgentHello.AgentVisibility.Value(self.agent.visibility)
        ), lambda msg: isinstance(msg, ServerHello))
        assert isinstance(server_hello, ServerHello)
        logger.info("Handshake successful")
        await self.agent.ready()
