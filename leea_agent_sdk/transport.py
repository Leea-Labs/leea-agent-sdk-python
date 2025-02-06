import asyncio
from functools import wraps
from os import getenv

from websockets import ConnectionClosedError, connect as ws_connect

from leea_agent_sdk.logger import logger


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

    def __init__(self):
        self._connect_uri = f"{getenv("LEEA_API_WS_HOST", "ws://localhost:8081")}/api/v1/connect"

    def on_connect(self, callback):
        self._connect_callbacks.append(callback)

    async def _get_connection(self):
        if self._connection is not None:
            return self._connection

        logger.debug(f"Connecting: {self._connect_uri}")
        self._connection = ws_connect(
            self._connect_uri,
            ping_interval=5,
            ping_timeout=1
        )
        for cb in self._connect_callbacks:
            if asyncio.iscoroutinefunction(cb):
                await cb(self)
            else:
                cb(self)

        return self._connection

    @reconnect_if_closed
    async def send(self, msg: bytes):
        (await self._get_connection()).send(msg)
        logger.debug(f"-> {msg}")

    @reconnect_if_closed
    async def receive(self) -> bytes:
        recv = (await self._get_connection()).recv()
        logger.debug(f"<- {recv}")
        return recv
