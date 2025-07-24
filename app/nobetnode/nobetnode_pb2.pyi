from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ("ip", "banDuration")
    IP_FIELD_NUMBER: _ClassVar[int]
    BANDURATION_FIELD_NUMBER: _ClassVar[int]
    ip: str
    banDuration: int
    def __init__(self, ip: _Optional[str] = ..., banDuration: _Optional[int] = ...) -> None: ...

class BanResult(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...
