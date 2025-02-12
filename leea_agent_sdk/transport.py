import asyncio
from os import getenv, getcwd

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

from leea_agent_sdk.protocol.protocol_pb2 import Envelope, DESCRIPTOR

from google.protobuf import message as _message
from google.protobuf import message_factory
from leea_agent_sdk.logger import logger

from leea_agent_sdk.web3_solana import Web3InstanceSolana


class Transport:
    _message_subscribers = []
    _connect_subscribers = []
    _connected = False
    _requests = {}
    _socket = None
    _requests_in_flight = {}

    def __init__(self, api_key=None, wallet_path=None):
        self._connect_uri = (
            f"{getenv('LEEA_API_WS_HOST', 'ws://localhost:1211')}/api/v1/connect"
        )
        self._api_key = api_key or getenv("LEEA_API_KEY")
        self._wallet = Web3InstanceSolana(
            wallet_path or getenv("LEEA_WALLET_PATH", f"{getcwd()}/wallet.json")
        )
        if not self._api_key:
            raise RuntimeError("Please provide LEEA_API_KEY")

    def subscribe_message(self, predicate, func, one_shot=False):
        self._message_subscribers.append((predicate, func, one_shot))

    def on_connected(self, func):
        self._connect_subscribers.append(func)

    async def _reader_loop(self, ws):
        async for packet in ws:
            message = self._unpack(packet)
            logger.debug(f"-> {message}")

            for predicate, future in self._requests_in_flight.items():
                if not future.done() and predicate(message):
                    future.set_result(message)

            for predicate, func, one_shot in self._message_subscribers[:]:
                if predicate(message):
                    if one_shot:
                        self._message_subscribers.remove((predicate, func, one_shot))
                    try:
                        if asyncio.iscoroutinefunction(func):
                            await func(self, message)
                        else:
                            func(self, message)
                    except Exception as e:
                        logger.exception(e)

    async def run(self):
        async for ws in connect(self._connect_uri, additional_headers={"Authorization": f"Bearer {self._api_key}"}):
            try:
                tasks = []
                if not self._connected:
                    logger.debug(f"Connected: {self._connect_uri}")
                    self._connected = True
                    self._socket = ws
                    for func in self._connect_subscribers:
                        tasks.append(asyncio.create_task(func(self)))
                tasks.append(self._reader_loop(ws))
                await asyncio.gather(*tasks)
            except ConnectionClosed:
                self._connected = False
                self._socket = None

    async def send(self, msg: _message.Message, wait_predicate: callable = None):
        packed = self._pack(msg)
        await self._socket.send(packed)
        logger.debug(f"<- {msg}")
        if wait_predicate:
            fut = asyncio.get_event_loop().create_future()
            self._requests_in_flight[wait_predicate] = fut
            return await fut

    def get_public_key(self):
        return self._wallet.get_public_key()

    def _pack(self, message: _message.Message) -> bytes:
        payload = message.SerializeToString()
        signature = self._wallet.sign_message(payload)
        envelope = Envelope(
            Type=Envelope.MessageType.Value(message.DESCRIPTOR.name),
            Payload=payload,
            PublicKey=self._wallet.get_public_key(),
            Signature=signature,
        )
        return envelope.SerializeToString()

    def _unpack(self, data: bytes) -> _message.Message:
        envelope = Envelope()
        envelope.ParseFromString(data)
        message_type = Envelope.MessageType.Name(envelope.Type)
        message_type = DESCRIPTOR.message_types_by_name[message_type]
        message = message_factory.GetMessageClass(message_type)()
        message.ParseFromString(envelope.Payload)
        return message
