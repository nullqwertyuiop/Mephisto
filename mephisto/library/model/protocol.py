from typing import Literal

from avilla.core import BaseProtocol
from avilla.onebot.v11 import (
    OneBot11ForwardConfig,
    OneBot11Protocol,
    OneBot11ReverseConfig,
)
from avilla.telegram.protocol import TelegramBotConfig, TelegramProtocol
from pydantic import AnyHttpUrl, BaseModel, ValidationError
from yarl import URL


class ProtocolConfig(BaseModel):
    protocol: str

    @property
    def id(self):
        return ...

    def to_protocol(self) -> BaseProtocol:
        pass

    @classmethod
    def resolve(cls, data: dict) -> "ProtocolConfig":
        for sub in cls.__subclasses__():
            try:
                return sub(**data)
            except ValidationError:
                continue
        raise ValueError(f"Unknown protocol: {data.get('protocol')!r}")


class TelegramBotProtocolConfig(ProtocolConfig):
    protocol: Literal["telegram"] = "telegram"
    token: str
    base_url: AnyHttpUrl = "https://api.telegram.org/bot"
    base_file_url: AnyHttpUrl = "https://api.telegram.org/file/bot"
    timeout: int = 15
    reformat: bool = False

    def to_protocol(self) -> TelegramProtocol:
        return TelegramProtocol().configure(
            TelegramBotConfig(
                token=self.token,
                base_url=URL(str(self.base_url)),
                base_file_url=URL(str(self.base_file_url)),
                timeout=self.timeout,
                reformat=self.reformat,
            )
        )

    @property
    def id(self):
        return self.token.split(":")[0]


class OneBotV11ProtocolFwdConfig(ProtocolConfig):
    protocol: Literal["onebot_v11_forward"] = "onebot_v11_forward"
    endpoint: AnyHttpUrl
    access_token: str | None = None

    def to_protocol(self) -> OneBot11Protocol:
        return OneBot11Protocol().configure(
            OneBot11ForwardConfig(
                endpoint=URL(str(self.endpoint)), access_token=self.access_token
            )
        )

    @property
    def id(self):
        return f"{self.endpoint.host}_{self.endpoint.port}"


class OneBotV11ProtocolRevConfig(ProtocolConfig):
    protocol: Literal["onebot_v11_reverse"] = "onebot_v11_reverse"
    endpoint: str
    access_token: str | None = None

    def to_protocol(self) -> OneBot11Protocol:
        return OneBot11Protocol().configure(
            OneBot11ReverseConfig(
                endpoint=self.endpoint, access_token=self.access_token
            )
        )

    @property
    def id(self):
        return self.endpoint.replace("/", "_")


class ElizabethProtocolConfig(ProtocolConfig):
    protocol: Literal["mirai-api-http"] = "mirai-api-http"
