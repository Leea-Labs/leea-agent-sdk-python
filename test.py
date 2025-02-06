import google.protobuf.any_pb2 as any
from google._upb._message import Message
from google.protobuf import message_factory

from leea_agent_sdk.protocol import pack, unpack
from leea_agent_sdk.protocol.protocol_pb2 import Envelope, ExecutionRequest, DESCRIPTOR, ExecutionResult

packed = pack(ExecutionResult(RequestID="2", ))
print(packed)
print(unpack(packed))
print(type(unpack(packed)))
