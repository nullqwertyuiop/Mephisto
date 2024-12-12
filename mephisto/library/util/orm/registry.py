import asyncio
from asyncio import Semaphore
from pathlib import Path
from typing import Any, Callable, Coroutine, Final

from avilla.core import Selector
from loguru import logger

from mephisto.library.util.orm.base import DatabaseEngine
from mephisto.shared import DATA_ROOT

SQLITE_LINK_PATTERN: Final[str] = "sqlite+aiosqlite:///{path}"
DATABASE_PATH: Final[Path] = DATA_ROOT / "database"


class DatabaseRegistry:
    databases: dict[str, DatabaseEngine]
    hooks: dict[str, list[Callable[[DatabaseEngine], Coroutine[None, None, None]]]]

    def __init__(self):
        self.databases = {}
        self.hooks = {}

    def __getitem__(self, selector: Selector) -> DatabaseEngine:
        if selector.display in self.databases:
            return self.databases[selector.display]
        return asyncio.run(self.create(selector))

    @staticmethod
    def selector_to_path(selector: Selector) -> Path:
        return Path(DATABASE_PATH / f"{'/'.join(selector.pattern.values())}.db")

    async def create(self, selector: Selector | str) -> DatabaseEngine:
        key = selector.display if isinstance(selector, Selector) else selector
        if key in self.databases:
            return self.databases[key]
        path = (
            self.selector_to_path(selector)
            if isinstance(selector, Selector)
            else Path(DATABASE_PATH / f"{key}.db")
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"[DatabaseRegistry] Creating database: {key}")
        self.databases[key] = DatabaseEngine(
            SQLITE_LINK_PATTERN.format(path=path), Semaphore(1)
        )
        await self._run_hooks(self.databases[key])
        return self.databases[key]

    async def _run_hooks(self, database: DatabaseEngine):
        for module in self.hooks:
            for hook in self.hooks[module]:
                try:
                    logger.debug(
                        f"[DatabaseRegistry] Running hook: {module}.{hook.__name__}"
                    )
                    await hook(database)
                except Exception as err:
                    logger.exception(err)
                    logger.error(
                        f"[DatabaseRegistry] Hook {module}.{hook.__name__} failed"
                    )

    def hook(self, func: Callable[[DatabaseEngine], Coroutine[Any, Any, None]]):
        self.hooks.setdefault(func.__module__, []).append(func)  # type: ignore
        logger.debug(f"[DatabaseRegistry] Registered hook: {func.__module__}.{func.__name__}")  # type: ignore
