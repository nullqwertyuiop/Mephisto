from abc import ABCMeta, abstractmethod
from os import PathLike
from typing import Literal

from avilla.core import BaseProtocol
from avilla.elizabeth.protocol import ElizabethConfig, ElizabethProtocol
from avilla.onebot.v11 import (
    OneBot11ForwardConfig,
    OneBot11Protocol,
    OneBot11ReverseConfig,
)
from avilla.qqapi.protocol import (
    QQAPIWebsocketConfig,
    QQAPIWebhookConfig,
    QQAPIProtocol,
)
from avilla.red.protocol import RedConfig, RedProtocol

# from avilla.satori.protocol import SatoriConfig, SatoriProtocol
from avilla.telegram.protocol import (
    TelegramLongPollingConfig,
    TelegramProtocol,
    TelegramWebhookConfig,
)
from pydantic import AnyHttpUrl, BaseModel, ValidationError
from yarl import URL


class ProtocolConfig(BaseModel, metaclass=ABCMeta):
    protocol: str
    enabled: bool = True

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @abstractmethod
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


class ElizabethProtocolConfig(ProtocolConfig):
    protocol: Literal["mirai-api-http"] = "mirai-api-http"
    qq: int
    host: str
    port: int
    access_token: str

    @property
    def id(self) -> str:
        return f"{self.host}_{self.port}"

    def to_protocol(self) -> ElizabethProtocol:
        return ElizabethProtocol().configure(
            ElizabethConfig(
                qq=self.qq,
                host=self.host,
                port=self.port,
                access_token=self.access_token,
            )
        )


class QQAPIWebsocketProtocolConfig(ProtocolConfig):
    protocol: Literal["qqapi_websocket"] = "qqapi_websocket"
    id: str
    token: str
    secret: str
    shard: tuple[int, int] | None = None
    is_sandbox: bool = False
    api_base: AnyHttpUrl = "https://api.sgroup.qq.com/"
    sandbox_api_base: AnyHttpUrl = "https://sandbox.api.sgroup.qq.com"
    auth_base: AnyHttpUrl = "https://bots.qq.com/app/getAppAccessToken"

    def to_protocol(self) -> QQAPIProtocol:
        return QQAPIProtocol().configure(
            QQAPIWebsocketConfig(
                id=self.id,
                token=self.token,
                secret=self.secret,
                shard=self.shard,
                is_sandbox=self.is_sandbox,
                api_base=URL(str(self.api_base)),
                sandbox_api_base=URL(str(self.sandbox_api_base)),
                auth_base=URL(str(self.auth_base)),
            )
        )

    @property
    def id(self) -> str:
        return self.id


class QQAPIWebhookProtocolConfig(ProtocolConfig):
    protocol: Literal["qqapi_webhook"] = "qqapi_webhook"
    secrets: dict[str, str]
    host: str = "0.0.0.0"
    port: int = 8080
    path: str = ""
    certfile: str | PathLike[str] | None = None
    keyfile: str | PathLike[str] | None = None
    verify_payload: bool = True
    is_sandbox: bool = False
    api_base: AnyHttpUrl = "https://api.sgroup.qq.com/"
    sandbox_api_base: AnyHttpUrl = "https://sandbox.api.sgroup.qq.com"
    auth_base: AnyHttpUrl = "https://bots.qq.com/app/getAppAccessToken"

    def to_protocol(self) -> QQAPIProtocol:
        return QQAPIProtocol().configure(
            QQAPIWebhookConfig(
                secrets=self.secrets,
                host=self.host,
                port=self.port,
                path=self.path,
                certfile=self.certfile,
                keyfile=self.keyfile,
                verify_payload=self.verify_payload,
                is_sandbox=self.is_sandbox,
                api_base=URL(str(self.api_base)),
                sandbox_api_base=URL(str(self.sandbox_api_base)),
                auth_base=URL(str(self.auth_base)),
            )
        )

    @property
    def id(self) -> str:
        return f"{self.host}_{self.port}"


class RedProtocolConfig(ProtocolConfig):
    protocol: Literal["red"] = "red"
    access_token: str
    host: str = "localhost"
    port: int = 16530

    def to_protocol(self) -> RedProtocol:
        return RedProtocol().configure(
            RedConfig(access_token=self.access_token, host=self.host, port=self.port)
        )

    @property
    def id(self) -> str:
        return f"{self.host}_{self.port}"


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


class TelegramBotLongPollingProtocolConfig(ProtocolConfig):
    protocol: Literal["telegram_long_polling"] = "telegram_long_polling"
    token: str
    base_url: AnyHttpUrl = "https://api.telegram.org"
    base_file_url: AnyHttpUrl = "https://api.telegram.org/file"
    timeout: int = 15

    def to_protocol(self) -> TelegramProtocol:
        return TelegramProtocol().configure(
            TelegramLongPollingConfig(
                token=self.token,
                base_url=URL(str(self.base_url)),
                file_base_url=URL(str(self.base_file_url)),
                timeout=self.timeout,
            )
        )

    @property
    def id(self):
        return self.token.split(":")[0]


class TelegramBotWebhookProtocolConfig(ProtocolConfig):
    protocol: Literal["telegram_webhook"] = "telegram_webhook"
    token: str
    webhook_url: AnyHttpUrl
    secret_token: str | None = None
    drop_pending_updates: bool = False
    base_url: AnyHttpUrl = "https://api.telegram.org"
    base_file_url: AnyHttpUrl = "https://api.telegram.org/file"

    def to_protocol(self) -> TelegramProtocol:
        return TelegramProtocol().configure(
            TelegramWebhookConfig(
                token=self.token,
                webhook_url=URL(str(self.webhook_url)),
                secret_token=self.secret_token,
                drop_pending_updates=self.drop_pending_updates,
                base_url=URL(str(self.base_url)),
                file_base_url=URL(str(self.base_file_url)),
            )
        )

    @property
    def id(self):
        return self.token.split(":")[0]
