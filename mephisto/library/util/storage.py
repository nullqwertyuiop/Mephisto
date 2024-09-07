import asyncio
from asyncio import TimerHandle
from datetime import timedelta
from hashlib import sha256
from pathlib import Path
from typing import IO
from uuid import uuid4

from creart import it
from loguru import logger

from mephisto.library.util.const import TEMPORARY_FILES_ROOT


def sha256_hash(data: IO[bytes], chunk_size: int = 4096) -> str:
    result = sha256()
    for chunk in iter(lambda: data.read(chunk_size), b""):
        result.update(chunk)
    return result.hexdigest()


class TemporaryFile:
    file: Path
    lifespan: timedelta | None
    _timer: TimerHandle | None

    def __init__(self, filetype: str | None = None, lifespan: timedelta | None = None):
        self.file = TEMPORARY_FILES_ROOT / uuid4().hex
        if filetype is not None:
            self.file = self.file.with_suffix(filetype)
        self.lifespan = lifespan
        logger.debug(f"Temporary file initialized: {self.file}")
        self._timer = None

    def unlink(self):
        self.file.unlink(missing_ok=True)

    @property
    def id(self):
        return self.file.name

    def __enter__(self):
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lifespan is not None:
            logger.debug(
                f"Eliminating temporary file: {self.file} in {self.lifespan.total_seconds()}s"
            )
            self._timer = it(asyncio.AbstractEventLoop).call_later(
                self.lifespan.total_seconds(), self.unlink
            )
        else:
            logger.debug(f"Eliminating temporary file: {self.file}")
            self.unlink()

    def __delete__(self, instance):
        if self._timer and not self._timer.cancelled():
            self._timer.cancel()
            self.unlink()


def fetch_file(*parts: str, scope: Path) -> Path | None:
    if any(True for part in parts if part.startswith("..") or not part):
        print("filtered")
        return None
    print(f"{parts = }")
    print(f"{next(scope.rglob(Path(*parts).as_posix()), None) = }")
    return next(scope.rglob(Path(*parts).as_posix()), None)
