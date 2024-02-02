from typing import Callable, Literal, NoReturn, TypeVar

from avilla.core import Context
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.depend import Depend
from graia.saya.factory import ensure_buffer

T_Callable = TypeVar("T_Callable", bound=Callable)


class ContextPattern:
    @classmethod
    def follows_all(cls, *patterns: str) -> Depend:
        async def check(ctx: Context) -> NoReturn:
            if all(ctx.client.follows(pattern) for pattern in patterns):
                return
            raise ExecutionStop()

        return Depend(check)

    @classmethod
    def follows_any(cls, *patterns: str) -> Depend:
        async def check(ctx: Context) -> NoReturn:
            if any(ctx.client.follows(pattern) for pattern in patterns):
                return
            raise ExecutionStop()

        return Depend(check)

    @classmethod
    def follows(cls, *patterns: str, method: Literal["all", "any"] = "all") -> Depend:
        return getattr(cls, f"follows_{method}")(*patterns)


def follows(*patterns: str, method: Literal["all", "any"] = "all"):
    def wrapper(func: T_Callable) -> T_Callable:
        buffer = ensure_buffer(func)
        buffer.setdefault("decorators", []).append(
            ContextPattern.follows(*patterns, method=method)
        )
        return func

    return wrapper
