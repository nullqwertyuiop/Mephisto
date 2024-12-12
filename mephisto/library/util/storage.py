import asyncio
from asyncio import TimerHandle
from contextlib import suppress
from datetime import datetime, timedelta
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from typing import IO
from uuid import uuid4

import filetype
from creart import it
from kayaku import create
from launart import Launart
from loguru import logger
from yarl import URL

from library.service import SessionService
from mephisto.library.model.config import MephistoConfig
from mephisto.library.util.const import (
    FILES_STORAGE_ROOT,
    TEMPORARY_FILE_ENDPOINT,
    TEMPORARY_FILES_ROOT,
)


def sha256_hash(data: IO[bytes], chunk_size: int = 4096) -> str:
    result = sha256()
    for chunk in iter(lambda: data.read(chunk_size), b""):
        result.update(chunk)
    return result.hexdigest()


class File:
    filename: str
    scope: Path

    def __init__(
        self,
        *parts: str,
        extension: str | None = None,
        scope: Path = FILES_STORAGE_ROOT,
    ):
        parts = [str(part) for part in parts if part]
        name = parts[-1]
        if extension:
            extension = extension.lstrip(".")
            self.filename = f"{name}.{extension}"
        else:
            self.filename = name
        self.scope = Path(scope, *parts[:-1])

    @property
    def path(self):
        return self.scope / f"{self.filename}"

    def ensure_parents(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write_text(self, text: str, encoding: str = "utf-8", **kwargs):
        self.ensure_parents()
        self.path.write_text(text, encoding=encoding, **kwargs)

    def read_text(self, encoding: str = "utf-8", **kwargs) -> str:
        return self.path.read_text(encoding=encoding, **kwargs)

    def write_bytes(self, data: bytes):
        self.ensure_parents()
        self.path.write_bytes(data)

    def read_bytes(self) -> bytes:
        return self.path.read_bytes()

    def update_extension(self, extension: str):
        self.path.rename(self.path.with_suffix(f".{extension.lstrip('.')}"))
        self.filename = self.path.name

    def touch(self):
        self.ensure_parents()
        self.path.touch()

    def unlink(self):
        self.path.unlink(missing_ok=True)

    @property
    def exists(self):
        return self.path.is_file()

    @property
    def created_time(self):
        return datetime.fromtimestamp(self.path.stat().st_ctime)

    @property
    def modified_time(self):
        return datetime.fromtimestamp(self.path.stat().st_mtime)

    @property
    def accessed_time(self):
        return datetime.fromtimestamp(self.path.stat().st_atime)

    @property
    def created_delta(self):
        return datetime.now() - self.created_time

    @property
    def modified_delta(self):
        return datetime.now() - self.modified_time

    @property
    def accessed_delta(self):
        return datetime.now() - self.accessed_time

    def __str__(self):
        return self.path.as_posix()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.path}>"


class TemporaryFile(File):
    """
    A temporary file that will be deleted after a
    certain amount of time, or when exiting the context,
    or when the program exits.
    """

    lifespan: timedelta | None
    _timer: TimerHandle | None

    def __init__(
        self,
        extension: str | None = None,
        lifespan: timedelta | None = None,
        file_hash: str | None = None,
    ):
        filename = file_hash if file_hash else uuid4().hex
        super().__init__(filename, extension=extension, scope=TEMPORARY_FILES_ROOT)
        self.lifespan = lifespan
        self._timer = None
        logger.debug(f"[{self.__class__.__name__}] File initialized: {self.path}")

    @property
    def file(self):
        return self.path

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        extension: str | None = None,
        lifespan: timedelta | None = None,
    ):
        if extension is None:
            with suppress(TypeError):
                extension = filetype.guess_extension(data)
        file_hash = sha256_hash(BytesIO(data))
        temp = cls(extension=extension, lifespan=lifespan, file_hash=file_hash)
        temp.file.write_bytes(data)
        return temp

    @classmethod
    def from_text(
        cls,
        text: str,
        extension: str | None = None,
        lifespan: timedelta | None = None,
    ):
        return cls.from_bytes(text.encode(), extension, lifespan)

    @classmethod
    def from_file(cls, file: Path | File, lifespan: timedelta | None = None):
        path = file if isinstance(file, Path) else file.path
        return cls.from_bytes(path.read_bytes(), lifespan=lifespan)

    @property
    def internal_url(self):
        cfg: MephistoConfig = create(MephistoConfig)
        return (
            "http://127.0.0.1:"
            + str(cfg.advanced.uvicorn_port)
            + TEMPORARY_FILE_ENDPOINT
            + f"?id={self.id}"
        )

    @property
    def external_url(self):
        cfg: MephistoConfig = create(MephistoConfig)
        return (
            f'{"https" if cfg.advanced.use_https else "http"}://'
            + cfg.advanced.domain
            + TEMPORARY_FILE_ENDPOINT
            + f"?id={self.id}"
        )

    def unlink(self):
        self.path.unlink(missing_ok=True)

    @property
    def id(self):
        return self.path.name

    def __enter__(self):
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lifespan is not None:
            logger.debug(
                f"[{self.__class__.__name__}] Eliminating file: {self.path} "
                f"in {self.lifespan.total_seconds()}s"
            )
            self._timer = it(asyncio.AbstractEventLoop).call_later(
                self.lifespan.total_seconds(), self.unlink  # type: ignore
            )
        else:
            logger.debug(f"[{self.__class__.__name__}] Eliminating file: {self.path}")
            self.unlink()

    def __delete__(self, instance):
        if self._timer and not self._timer.cancelled():
            self._timer.cancel()
            self.unlink()


def fetch_file(*parts: str, scope: Path) -> Path | None:
    if any(True for part in parts if part.startswith("..") or not part):
        return None
    return next(scope.rglob(Path(*parts).as_posix()), None)


def fetch_attachment(hashed: str) -> Path | None:
    return fetch_file(hashed[:2], hashed[2:4], hashed[4:], scope=TEMPORARY_FILES_ROOT)


async def download_file(
    url: URL | str, session_name: str = "universal", **kwargs
) -> bytes:
    async with (
        it(Launart)
        .get_component(SessionService)
        .get(session_name)
        .get(url, **kwargs) as res
    ):
        return await res.read()
