import asyncio
import os
import time
from functools import wraps
from os import getenv

from websockets.exceptions import ConnectionClosedError
from websockets.asyncio.client import connect
from websockets.protocol import State
from google.protobuf import message as _message

from leea_agent_sdk.logger import logger
from leea_agent_sdk.protocol.protocol_pb2 import DESCRIPTOR, Envelope
from leea_agent_sdk.web3 import Web3Instance
from google.protobuf import message_factory


def reconnect_if_closed(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except ConnectionClosedError:
            logger.warn("Connection error, will reconnect")
            self._connection = None
            return method(self, *args, **kwargs)

    return wrapper


class Transport:
    _connection = None
    _connect_callbacks = []

    def __init__(self, api_key=None):
        self._connect_uri = f"{getenv('LEEA_API_WS_HOST', 'ws://localhost:8081')}/api/v1/connect"
        self._api_key = api_key or getenv("LEEA_API_KEY")
        self._wallet = Web3Instance(getenv('LEEA_WALLET_PATH', f"{os.getcwd()}/wallet.json"))
        if not self._api_key:
            raise RuntimeError("Please provide LEEA_API_KEY")

    def on_connect(self, callback):
        self._connect_callbacks.append(callback)

    async def _get_connection(self, retry=5):
        if self._connection is not None:
            return self._connection

        logger.debug(f"Connecting: {self._connect_uri}")
        tries = retry
        while tries > 0:
            try:
                connection = await connect(
                    self._connect_uri,
                    ping_interval=5,
                    ping_timeout=1,
                    additional_headers={
                        'Authorization': f"Bearer {self._api_key}"
                    }
                )
                if connection.state == State.OPEN:
                    self._connection = connection
                    break
                else:
                    raise OSError("Connection closed by server")
            except OSError:
                tries -= 1
                time.sleep(1)
        if self._connection is None:
            raise ConnectionError("Cannot connect to API server")
        for cb in self._connect_callbacks:
            if asyncio.iscoroutinefunction(cb):
                await cb()
            else:
                cb()

        return self._connection

    @reconnect_if_closed
    async def send(self, msg: _message.Message):
        packed = self._pack(msg)
        await (await self._get_connection()).send(packed)
        logger.debug(f"-> {msg}")

    @reconnect_if_closed
    async def receive(self) -> _message.Message:
        recv = await (await self._get_connection()).recv()
        msg = self._unpack(recv)
        logger.debug(f"<- {msg}")
        return msg

    def get_public_key(self):
        return self._wallet.get_public_key()

    def _pack(self, message: _message.Message) -> bytes:
        payload = message.SerializeToString()
        public_key, signature = self._wallet.sign_message(payload)
        envelope = Envelope(
            Type=Envelope.MessageType.Value(message.DESCRIPTOR.name),
            Payload=payload,
            PublicKey=public_key,
            Signature=signature
        )
        return envelope.SerializeToString()

    def _unpack(self, data: bytes) -> _message.Message:
        envelope = Envelope()
        envelope.ParseFromString(data)
        assert self._wallet.verify_message(envelope.Payload, envelope.Signature), "Message signature is not valid"

        message_type = Envelope.MessageType.Name(envelope.Type)
        message_type = DESCRIPTOR.message_types_by_name[message_type]
        message = message_factory.GetMessageClass(message_type)()
        message.ParseFromString(envelope.Payload)
        return message
