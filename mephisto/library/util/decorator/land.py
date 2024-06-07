from typing import Callable, NoReturn, TypeVar

from avilla.core import Context
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.depend import Depend
from graia.saya.factory import ensure_buffer

T_Callable = TypeVar("T_Callable", bound=Callable)


class Land:
    @classmethod
    def include(cls, *lands: str) -> Depend:
        async def check(ctx: Context) -> NoReturn:
            if ctx.land.name.lower() not in lands:
                raise ExecutionStop()

        return Depend(check)

    @classmethod
    def exclude(cls, *lands: str) -> Depend:
        async def check(ctx: Context) -> NoReturn:
            if ctx.land.name.lower() in lands:
                raise ExecutionStop()

        return Depend(check)


def include(*lands: str):
    def wrapper(func: T_Callable) -> T_Callable:
        buffer = ensure_buffer(func)
        buffer.setdefault("decorators", []).append(Land.include(*lands))
        return func

    return wrapper


def exclude(*lands: str):
    def wrapper(func: T_Callable) -> T_Callable:
        buffer = ensure_buffer(func)
        buffer.setdefault("decorators", []).append(Land.exclude(*lands))
        return func

    return wrapper
