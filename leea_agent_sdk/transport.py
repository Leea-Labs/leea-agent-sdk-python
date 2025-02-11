import json
from functools import wraps

from websockets import ConnectionClosedError
from websockets.sync.client import connect as ws_connect

from leea_agent_sdk.logger import logger
from leea_agent_sdk.protocol import messages, ProtoMessage


def reconnect_if_closed(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except ConnectionClosedError:
            logger.warning("Connection error, reconnecting...")
            self.connection = self.connect()
            return method(self, *args, **kwargs)

    return wrapper


class Transport:
    def __init__(self, agent_name):
        logger.info(f"Connecting {agent_name}")
        self.agent_name = agent_name
        self.connection = self.connect()

    def connect(self):
        return ws_connect("ws://localhost:8081/api/v1/connect", additional_headers={"AGENT_NAME": self.agent_name})

    @reconnect_if_closed
    def send(self, msg: ProtoMessage):
        self.connection.send(msg.model_dump_json())

    @reconnect_if_closed
    def receive(self) -> ProtoMessage:
        data = json.loads(self.connection.recv())
        return messages.validate_json(data)
