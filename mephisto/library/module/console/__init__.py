from avilla.console.element import Markdown
from avilla.core import BaseAccount, Context, Selector
from avilla.standard.core.account import AccountAvailable
from avilla.standard.core.message import MessageReceived
from avilla.twilight.twilight import FullMatch, Twilight
from graia.broadcast import PropagationCancelled
from graia.saya.builtins.broadcast.shortcut import dispatch, listen

from mephisto.library.util.const import LandType
from mephisto.library.util.decorator import include

_HELLO_TEXT = """
# Mephisto

Welcome to Mephisto console!

Type `/help` to get help.
"""


@listen(AccountAvailable)
async def startup(account: BaseAccount):
    if (land := account.route.pattern["land"]) != LandType.CONSOLE:
        return
    scene = account.get_context(Selector().land(land).user("console")).scene
    await scene.send_message(Markdown(_HELLO_TEXT, justify="center"))


_HELP_TEXT = """
# Mephisto Help Desk

Help is not available now.
"""


@listen(MessageReceived)
@include(LandType.CONSOLE)
@dispatch(Twilight(FullMatch("/help")))
async def console_help(ctx: Context):
    await ctx.scene.send_message(_HELP_TEXT)
    raise PropagationCancelled()
