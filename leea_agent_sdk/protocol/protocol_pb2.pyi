from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Envelope(_message.Message):
    __slots__ = ("Type", "Payload")
    class MessageType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AgentHello: _ClassVar[Envelope.MessageType]
        ServerHello: _ClassVar[Envelope.MessageType]
        ExecutionRequest: _ClassVar[Envelope.MessageType]
        ExecutionResult: _ClassVar[Envelope.MessageType]
        ExecutionLog: _ClassVar[Envelope.MessageType]
        Error: _ClassVar[Envelope.MessageType]
    AgentHello: Envelope.MessageType
    ServerHello: Envelope.MessageType
    ExecutionRequest: Envelope.MessageType
    ExecutionResult: Envelope.MessageType
    ExecutionLog: Envelope.MessageType
    Error: Envelope.MessageType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    Type: Envelope.MessageType
    Payload: bytes
    def __init__(self, Type: _Optional[_Union[Envelope.MessageType, str]] = ..., Payload: _Optional[bytes] = ...) -> None: ...

class AgentHello(_message.Message):
    __slots__ = ("Name", "Description", "InputSchema", "OutputSchema", "PublicKey", "Signature")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INPUTSCHEMA_FIELD_NUMBER: _ClassVar[int]
    OUTPUTSCHEMA_FIELD_NUMBER: _ClassVar[int]
    PUBLICKEY_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    Name: str
    Description: str
    InputSchema: str
    OutputSchema: str
    PublicKey: str
    Signature: str
    def __init__(self, Name: _Optional[str] = ..., Description: _Optional[str] = ..., InputSchema: _Optional[str] = ..., OutputSchema: _Optional[str] = ..., PublicKey: _Optional[str] = ..., Signature: _Optional[str] = ...) -> None: ...

class ServerHello(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Error(_message.Message):
    __slots__ = ("RequestID", "Message")
    REQUESTID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RequestID: str
    Message: str
    def __init__(self, RequestID: _Optional[str] = ..., Message: _Optional[str] = ...) -> None: ...

class ExecutionRequest(_message.Message):
    __slots__ = ("RequestID", "AgentID", "Input")
    REQUESTID_FIELD_NUMBER: _ClassVar[int]
    AGENTID_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    RequestID: str
    AgentID: str
    Input: str
    def __init__(self, RequestID: _Optional[str] = ..., AgentID: _Optional[str] = ..., Input: _Optional[str] = ...) -> None: ...

class ExecutionLog(_message.Message):
    __slots__ = ("RequestID", "Message")
    REQUESTID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RequestID: str
    Message: str
    def __init__(self, RequestID: _Optional[str] = ..., Message: _Optional[str] = ...) -> None: ...

class ExecutionResult(_message.Message):
    __slots__ = ("RequestID", "IsSuccessful", "Result")
    REQUESTID_FIELD_NUMBER: _ClassVar[int]
    ISSUCCESSFUL_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    RequestID: str
    IsSuccessful: bool
    Result: str
    def __init__(self, RequestID: _Optional[str] = ..., IsSuccessful: bool = ..., Result: _Optional[str] = ...) -> None: ...
