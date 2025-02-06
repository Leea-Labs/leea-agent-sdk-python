from google.protobuf import message as _message
from leea_agent_sdk.protocol.protocol_pb2 import Envelope, DESCRIPTOR
from google.protobuf import message_factory


def pack(message: _message.Message) -> bytes:
    envelope = Envelope(
        Type=Envelope.MessageType.Value(message.DESCRIPTOR.name),
        Payload=message.SerializeToString()
    )
    return envelope.SerializeToString()


def unpack(data: bytes) -> _message.Message:
    envelope = Envelope()
    envelope.ParseFromString(data)
    message_type = Envelope.MessageType.keys()[envelope.Type]
    message_type = DESCRIPTOR.message_types_by_name[message_type]
    message = message_factory.GetMessageClass(message_type)()
    message.ParseFromString(envelope.Payload)
    return message
