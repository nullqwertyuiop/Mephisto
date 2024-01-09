from avilla.core import Context
from avilla.standard.core.message import MessageReceived
from avilla.twilight.twilight import FullMatch, Twilight
from graia.saya.builtins.broadcast.shortcut import dispatch, listen

from mephisto.library.util.const import LandType
from mephisto.library.util.decorator import exclude


@listen(MessageReceived)
@dispatch(Twilight(FullMatch("/ping")))
@exclude(LandType.CONSOLE)
async def ping(ctx: Context):
    return await ctx.scene.send_message("pong")
