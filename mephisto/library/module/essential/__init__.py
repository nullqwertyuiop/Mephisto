from avilla.core import Avilla
from avilla.standard.core.message import MessageReceived
from graia.saya.builtins.broadcast.shortcut import listen

from mephisto.library.service.cache import MessageCacheService


@listen(MessageReceived)
async def cache_message(avilla: Avilla, event: MessageReceived):
    await avilla.launch_manager.get_component(MessageCacheService).add(event.message)
