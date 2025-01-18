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
    hello = AgentHello(
        Name=agent.name,
        Description=agent.description,
        InputSchema=json.dumps(agent.input_schema.model_json_schema()),
        OutputSchema=json.dumps(agent.output_schema.model_json_schema())
    )

    async def handshake(ts: Transport):
        logger.info("Handshaking")
        await ts.send(protocol.pack(hello))
        server_hello = protocol.unpack(await ts.receive())
        assert isinstance(server_hello, ServerHello)
        logger.info("Handshake successful")

    if transport is None:
        transport = Transport()
    transport.on_connect(handshake)
    agent.set_transport(transport)

    while True:
        logger.info("Waiting for execution request")
        message = protocol.unpack(await transport.receive())
        if isinstance(message, ExecutionRequest):
            logger.info("Processing request")
            Thread(
                target=asyncio.run,
                args=(_handle_execution_request(transport, agent, message),),
                daemon=True
            ).start()


async def _handle_execution_request(transport: Transport, agent: Agent, request: ExecutionRequest):
    logger.info(f"Execute request {request.RequestID}")
    input_obj = agent.input_schema.model_validate_json(request.Input)
    result = "{}"
    try:
        success = True
        output = await agent.run(input_obj)
        if isinstance(output, agent.output_schema):
            result = output.model_dump_json()
        else:
            logger.warn(f"Output is not instance of {type(agent.output_schema)}!")
            result = json.dumps(output)
    except Exception as e:
        logger.exception(e)
        success = False
    logger.info(f"[RequestID={request.RequestID}] {"Success" if success else "Fail"}: {result}")
    message = ExecutionResult(RequestID=request.RequestID, Result=result, IsSuccessful=success)
    await transport.send(protocol.pack(message))
