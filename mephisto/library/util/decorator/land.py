from typing import Callable, NoReturn, TypeVar

from avilla.core import Context
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.depend import Depend
from graia.saya.factory import ensure_buffer

from mephisto.library.util.const import LandType

T_Callable = TypeVar("T_Callable", bound=Callable)


class Land:
    # TODO: deprecate LandType
    @classmethod
    def include(cls, *lands: LandType) -> Depend:
        async def check(ctx: Context) -> NoReturn:
            if ctx.land.name.lower() in lands:
                return
            raise ExecutionStop()

        return Depend(check)

    @classmethod
    def exclude(cls, *lands: LandType) -> Depend:
        async def check(ctx: Context) -> NoReturn:
            if ctx.land.name.lower() in lands:
                raise ExecutionStop()
            return

        return Depend(check)


def include(*lands: LandType):
    def wrapper(func: T_Callable) -> T_Callable:
        buffer = ensure_buffer(func)
        buffer.setdefault("decorators", []).append(Land.include(*lands))
        return func

    return wrapper


def exclude(*lands: LandType):
    def wrapper(func: T_Callable) -> T_Callable:
        buffer = ensure_buffer(func)
        buffer.setdefault("decorators", []).append(Land.exclude(*lands))
        return func

    return wrapper
