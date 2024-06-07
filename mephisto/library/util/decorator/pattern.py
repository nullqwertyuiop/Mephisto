from typing import Callable, Literal, NoReturn, TypeVar

from avilla.core import Context
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.depend import Depend
from graia.saya.factory import ensure_buffer

T_Callable = TypeVar("T_Callable", bound=Callable)


class ContextPattern:
    @classmethod
    def follows_all(
        cls,
        *patterns: str,
        scope: Literal["account", "client", "endpoint", "scene", "self"] = "client",
    ) -> Depend:
        async def check(ctx: Context) -> NoReturn:
            selector = getattr(ctx, scope)
            if not all(selector.follows(pattern) for pattern in patterns):
                raise ExecutionStop()

        return Depend(check)

    @classmethod
    def follows_any(
        cls,
        *patterns: str,
        scope: Literal["account", "client", "endpoint", "scene", "self"] = "client",
    ) -> Depend:
        async def check(ctx: Context) -> NoReturn:
            selector = getattr(ctx, scope)
            if not any(selector.follows(pattern) for pattern in patterns):
                raise ExecutionStop()

        return Depend(check)

    @classmethod
    def follows(
        cls,
        *patterns: str,
        method: Literal["all", "any"] = "all",
        scope: Literal["account", "client", "endpoint", "scene", "self"] = "client",
    ) -> Depend:
        return getattr(cls, f"follows_{method}")(*patterns, **{"scope": scope})

    @classmethod
    def as_is_all(
        cls,
        *patterns: str,
        scope: Literal["account", "client", "endpoint", "scene", "self"] = "client",
    ) -> Depend:
        async def check(ctx: Context) -> NoReturn:
            selector = getattr(ctx, scope).display
            if not all(selector == pattern for pattern in patterns):
                raise ExecutionStop()

        return Depend(check)

    @classmethod
    def as_is_any(
        cls,
        *patterns: str,
        scope: Literal["account", "client", "endpoint", "scene", "self"] = "client",
    ) -> Depend:
        async def check(ctx: Context) -> NoReturn:
            selector = getattr(ctx, scope).display
            if not any(selector == pattern for pattern in patterns):
                raise ExecutionStop()

        return Depend(check)

    @classmethod
    def as_is(
        cls,
        *patterns: str,
        method: Literal["all", "any"] = "all",
        scope: Literal["account", "client", "endpoint", "scene", "self"] = "client",
    ) -> Depend:
        return getattr(cls, f"as_is_{method}")(*patterns, **{"scope": scope})


def follows(
    *patterns: str,
    method: Literal["all", "any"] = "all",
    scope: Literal["account", "client", "endpoint", "scene", "self"] = "client",
):
    def wrapper(func: T_Callable) -> T_Callable:
        buffer = ensure_buffer(func)
        buffer.setdefault("decorators", []).append(
            ContextPattern.follows(*patterns, method=method, scope=scope)
        )
        return func

    return wrapper


def as_is(
    *patterns: str,
    method: Literal["all", "any"] = "all",
    scope: Literal["account", "client", "endpoint", "scene", "self"] = "client",
):
    def wrapper(func: T_Callable) -> T_Callable:
        buffer = ensure_buffer(func)
        buffer.setdefault("decorators", []).append(
            ContextPattern.as_is(*patterns, method=method, scope=scope)
        )
        return func

    return wrapper


def account_follows(
    *patterns: str, method: Literal["all", "any"] = "all"
) -> Callable[[T_Callable], T_Callable]:
    return follows(*patterns, method=method, scope="account")


def account_as_is(
    *patterns: str, method: Literal["all", "any"] = "all"
) -> Callable[[T_Callable], T_Callable]:
    return as_is(*patterns, method=method, scope="account")


def client_follows(
    *patterns: str, method: Literal["all", "any"] = "all"
) -> Callable[[T_Callable], T_Callable]:
    return follows(*patterns, method=method, scope="client")


def client_as_is(
    *patterns: str, method: Literal["all", "any"] = "all"
) -> Callable[[T_Callable], T_Callable]:
    return as_is(*patterns, method=method, scope="client")


def endpoint_follows(
    *patterns: str, method: Literal["all", "any"] = "all"
) -> Callable[[T_Callable], T_Callable]:
    return follows(*patterns, method=method, scope="endpoint")


def endpoint_as_is(
    *patterns: str, method: Literal["all", "any"] = "all"
) -> Callable[[T_Callable], T_Callable]:
    return as_is(*patterns, method=method, scope="endpoint")


def scene_follows(
    *patterns: str, method: Literal["all", "any"] = "all"
) -> Callable[[T_Callable], T_Callable]:
    return follows(*patterns, method=method, scope="scene")


def scene_as_is(
    *patterns: str, method: Literal["all", "any"] = "all"
) -> Callable[[T_Callable], T_Callable]:
    return as_is(*patterns, method=method, scope="scene")


def self_follows(
    *patterns: str, method: Literal["all", "any"] = "all"
) -> Callable[[T_Callable], T_Callable]:
    return follows(*patterns, method=method, scope="self")


def self_as_is(
    *patterns: str, method: Literal["all", "any"] = "all"
) -> Callable[[T_Callable], T_Callable]:
    return as_is(*patterns, method=method, scope="self")
