from leea_agent_sdk.protocol import pack, unpack
from leea_agent_sdk.protocol.protocol_pb2 import ExecutionResult


def test_protocol_packing():
    packed = pack(ExecutionResult(RequestID="2", ))
    assert isinstance(packed, bytes)
    unpacked = unpack(packed)
    assert isinstance(unpacked, ExecutionResult)
    assert unpacked.RequestID == '2'
