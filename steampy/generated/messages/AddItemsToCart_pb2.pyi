from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Payload(_message.Message):
    __slots__ = ("country", "items", "nav_data")
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    NAV_DATA_FIELD_NUMBER: _ClassVar[int]
    country: str
    items: Items
    nav_data: NavData
    def __init__(
        self,
        country: _Optional[str] = ...,
        items: _Optional[_Union[Items, _Mapping]] = ...,
        nav_data: _Optional[_Union[NavData, _Mapping]] = ...,
    ) -> None: ...

class Items(_message.Message):
    __slots__ = ("packageid",)
    PACKAGEID_FIELD_NUMBER: _ClassVar[int]
    packageid: int
    def __init__(self, packageid: _Optional[int] = ...) -> None: ...

class NavData(_message.Message):
    __slots__ = (
        "domain",
        "controller",
        "method",
        "sub_method",
        "feature",
        "depth",
        "country_code",
        "web_key",
        "is_client",
        "curator_data",
        "is_likely_bot",
        "is_utm",
    )
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    CONTROLLER_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    SUB_METHOD_FIELD_NUMBER: _ClassVar[int]
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_CODE_FIELD_NUMBER: _ClassVar[int]
    WEB_KEY_FIELD_NUMBER: _ClassVar[int]
    IS_CLIENT_FIELD_NUMBER: _ClassVar[int]
    CURATOR_DATA_FIELD_NUMBER: _ClassVar[int]
    IS_LIKELY_BOT_FIELD_NUMBER: _ClassVar[int]
    IS_UTM_FIELD_NUMBER: _ClassVar[int]
    domain: str
    controller: str
    method: str
    sub_method: str
    feature: str
    depth: int
    country_code: str
    web_key: int
    is_client: int
    curator_data: str
    is_likely_bot: int
    is_utm: int
    def __init__(
        self,
        domain: _Optional[str] = ...,
        controller: _Optional[str] = ...,
        method: _Optional[str] = ...,
        sub_method: _Optional[str] = ...,
        feature: _Optional[str] = ...,
        depth: _Optional[int] = ...,
        country_code: _Optional[str] = ...,
        web_key: _Optional[int] = ...,
        is_client: _Optional[int] = ...,
        curator_data: _Optional[str] = ...,
        is_likely_bot: _Optional[int] = ...,
        is_utm: _Optional[int] = ...,
    ) -> None: ...
