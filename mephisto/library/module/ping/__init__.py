from avilla.core import Context
from avilla.standard.core.message import MessageReceived
from graia.amnesia.message import MessageChain
from graia.saya.builtins.broadcast.shortcut import listen


@listen(MessageReceived)
async def ping(ctx: Context, content: MessageChain):
    if str(content) == "/ping":
        return await ctx.scene.send_message("pong")
