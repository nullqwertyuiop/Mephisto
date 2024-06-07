from avilla.core import Selector, Message
from creart import it
from launart import Launart

from mephisto.library.service import MessageCacheService


async def fetch_cached_message(selector: Selector) -> Message | None:
    return await it(Launart).get_component(MessageCacheService).get(selector)
