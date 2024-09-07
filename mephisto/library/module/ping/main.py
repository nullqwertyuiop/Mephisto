from avilla.core import Context
from avilla.standard.core.message import MessageReceived
from avilla.twilight.twilight import Twilight, FullMatch
from graia.saya.builtins.broadcast.shortcut import listen, dispatch
from graiax.fastapi.saya.route import get

from mephisto.library.util.decorator import exclude
from mephisto.shared.model import GenericSuccessResponse


@listen(MessageReceived)
@dispatch(Twilight(FullMatch("/ping")))
@exclude("console")
async def ping(ctx: Context):
    return await ctx.scene.send_message("pong")


@get("/ping")
async def web_ping() -> GenericSuccessResponse:
    return GenericSuccessResponse(message="pong")
