import asyncio
from datetime import timedelta
from heapq import heappop
from time import time
from typing import Any

from avilla.core import Message, Selector
from graia.amnesia.builtins.memcache import Memcache
from kayaku import create
from launart import Launart, Service
from loguru import logger

from mephisto.library.model.config import MephistoConfig


class MessageCacheService(Service):
    id = "mephisto.service/cache"

    interval: float
    size: int
    lifespan: timedelta
    _cache: dict[str, tuple[float | None, Any]]
    expire: list[tuple[float, str]]

    __KEY_TEMPLATE = "mephisto.service/cache::{key}"

    def __init__(
        self,
        interval: float = 0.1,
        size: int = None,
        lifespan: timedelta = timedelta(hours=1),
        cache: dict[str, tuple[float | None, Any]] = None,
        expire: list[tuple[float, str]] = None,
    ):
        self.interval = interval
        if size is None:
            size: int = create(MephistoConfig).advanced.message_cache_size
        self.size = size
        self.lifespan = lifespan
        self._cache = cache or {}
        self.expire = expire or []
        super().__init__()

    @property
    def required(self):
        return {"mephisto.service/config"}

    @property
    def stages(self):
        return {"blocking"}

    @property
    def cache(self):
        return Memcache(self._cache, self.expire)

    async def add(self, message: Message):
        selector = message.to_selector()
        key = self.__KEY_TEMPLATE.format(key=selector.display)
        await self.cache.set(key, message, self.lifespan)

    async def get(self, selector: Selector) -> Message:
        key = self.__KEY_TEMPLATE.format(key=selector.display)
        return await self.cache.get(key)

    async def launch(self, manager: Launart):
        logger.info(f"[MessageCacheService] Initialized with {self.size} cache size")

        async with self.stage("blocking"):
            while not manager.status.exiting:
                while self.expire and (
                    self.expire[0][0] <= time() or len(self.expire) > self.size
                ):
                    _, key = heappop(self.expire)
                    self._cache.pop(key, None)
                await asyncio.sleep(self.interval)
