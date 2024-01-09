from avilla.core import Context
from avilla.standard.core.message import MessageReceived
from avilla.twilight.twilight import FullMatch, Twilight
from graia.saya.builtins.broadcast.shortcut import dispatch, listen


@listen(MessageReceived)
@dispatch(Twilight(FullMatch("/ping")))
async def ping(ctx: Context):
    return await ctx.scene.send_message("pong")
