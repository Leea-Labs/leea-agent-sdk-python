# import asyncio
#
# from leea_agent_sdk.agent import Agent
# from leea_agent_sdk.protocol import AgentHello, RunRequest
# from leea_agent_sdk.transport import Transport
# from leea_agent_sdk.logger import logger
#
#
# def ___register(_agent: Agent):
#     hello = AgentHello(
#         name=_agent.name,
#         description=_agent.description,
#         input_schema=_agent.input_schema.model_json_schema(),
#         output_schema=_agent.output_schema.model_json_schema()
#     )
#     _transport = Transport(_agent.name)
#     logger.info("Handshaking")
#     _transport.send(hello)
#     return _transport
#
#
# def start(_agent: Agent):
#     _transport = ___register(_agent)
#
#     is_async = asyncio.iscoroutinefunction(_agent.run)
#     logger.info("Waiting for run request")
#     while True:
#         msg = _transport.receive()
#         if isinstance(msg, RunRequest):
#             logger.info("New run request")
#             if is_async:
#                 asyncio.run(_agent.run(msg))
#             else:
#                 _agent.run(msg)
#         else:
#             print(msg)
#             print(type(msg))
