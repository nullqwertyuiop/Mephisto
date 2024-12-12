import asyncio
import contextlib
import os
import random
import signal
import socket
import string
import subprocess
import sys
import time
from contextvars import ContextVar
from http import HTTPStatus
from typing import cast

from creart import it
from fastapi import FastAPI, HTTPException
from graia.amnesia.builtins.asgi import UvicornASGIService
from graia.amnesia.builtins.asgi.asgitypes import ASGI3Application
from graiax.fastapi import FastAPIService
from launart import Launart, Service
from loguru import logger
from psutil import Process
from starlette.middleware.cors import CORSMiddleware

from mephisto.shared import LOG_ROOT, GenericSuccessResponse, setup_logger

setup_logger(LOG_ROOT / "daemon", 7)

fastapi = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
fastapi.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
token_ctx: ContextVar[str | None] = ContextVar("mephisto_daemon_token", default=None)


def setup_token():
    random.seed()
    token_ctx.set("".join(random.choices(string.ascii_letters + string.digits, k=32)))
    logger.debug(f"Generated token: {token_ctx.get()}")


def port_in_use(port) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("localhost", port))
        return False
    except socket.error:
        return True
    finally:
        sock.close()


def get_unoccupied_port() -> int:
    while True:
        port = random.randint(10000, 65535)
        if not port_in_use(port):
            return port


@fastapi.get("/daemon/regen_token")
async def regen_token(token: str):
    if token != token_ctx.get():
        raise HTTPException(403, "Invalid token")
    logger.info("Daemon Command received: regen_token")
    setup_token()
    return GenericSuccessResponse(
        code=HTTPStatus.OK,
        type="success",
        message="Token regenerated",
        data={"token": token_ctx.get()},
    )


@fastapi.get("/daemon/shutdown")
async def daemon_shutdown(token: str):
    if token != token_ctx.get():
        raise HTTPException(403, "Invalid token")
    logger.info("Daemon Command received: shutdown")
    proc_manager.keep_alive = False
    with contextlib.suppress(MephistoNotRunning):
        proc_manager.shutdown()
    loop = asyncio.get_running_loop()
    loop.call_later(
        1,
        signal.raise_signal,
        signal.SIGINT if sys.platform != "win32" else signal.CTRL_C_EVENT,
    )
    return GenericSuccessResponse(
        code=HTTPStatus.OK,
        type="success",
        message="Daemon shutdown",
    )


@fastapi.get("/command/shutdown")
async def shutdown(token: str):
    if token != token_ctx.get():
        raise HTTPException(403, "Invalid token")
    logger.info("Command received: shutdown")
    proc_manager.keep_alive = False
    try:
        proc_manager.shutdown()
    except MephistoNotRunning as e:
        raise HTTPException(400, "Mephisto not running") from e
    return GenericSuccessResponse(
        code=HTTPStatus.OK,
        type="success",
        message="Mephisto shutdown",
    )


@fastapi.get("/command/boot")
async def boot(token: str, keep_alive: bool = True):
    if token != token_ctx.get():
        raise HTTPException(403, "Invalid token")
    logger.info("Command received: boot")
    proc_manager.keep_alive = keep_alive
    try:
        proc_manager.boot()
    except MephistoAlreadyRunning as e:
        raise HTTPException(400, "Mephisto already running") from e
    return GenericSuccessResponse(
        code=HTTPStatus.OK,
        type="success",
        message="Mephisto booted",
    )


@fastapi.get("/command/reboot")
async def restart(token: str, keep_alive: bool = True):
    if token != token_ctx.get():
        raise HTTPException(403, "Invalid token")
    logger.info("Command received: restart")
    proc_manager.keep_alive = keep_alive
    try:
        proc_manager.restart()
    except MephistoNotRunning as e:
        raise HTTPException(400, "Mephisto not running") from e
    return GenericSuccessResponse(
        code=HTTPStatus.OK,
        type="success",
        message="Mephisto restarted",
    )


class MephistoAlreadyRunning(Exception):
    pass


class MephistoNotRunning(Exception):
    pass


class ProcessManager:
    proc: Process | None
    keep_alive: bool
    attempts: list

    def __init__(self):
        self.proc = None
        self.keep_alive = True
        self.attempts = []

    @staticmethod
    def run(*args, **kwargs) -> subprocess.Popen:
        return subprocess.Popen(*args, **kwargs)

    def boot(self):
        if self.proc is not None and self.proc.is_running():
            raise MephistoAlreadyRunning()
        popen = self.run(
            ["pdm", "run", "python", "__main__.py"],
            cwd="mephisto",
            env=os.environ | {"MEPHISTO_DAEMON_TOKEN": token_ctx.get()},
        )
        self.proc = Process(popen.pid)

    def shutdown(self):
        if self.proc is None or not self.proc.is_running():
            raise MephistoNotRunning()
        self.proc.send_signal(
            signal.SIGINT if sys.platform != "win32" else signal.CTRL_C_EVENT
        )
        self.proc.wait()
        self.proc = None

    def restart(self):
        self.shutdown()
        self.boot()

    def keep(self):
        if self.proc is None or not self.proc.is_running():
            self.check_and_add_attempt()
            if not self.keep_alive:
                return
            logger.warning("[MephistoDaemon] Mephisto 未运行，正在启动...")
            self.boot()

    def check_and_add_attempt(self):
        attempts_one_minute = [
            attempt for attempt in self.attempts if attempt > time.time() - 60
        ]
        if len(attempts_one_minute) >= 3:
            self.keep_alive = False
            logger.critical(
                "[MephistoDaemon] Mephisto 短时间内重启次数过多，已停止自动重启"
            )
            logger.critical("[MephistoDaemon] 请检查 Mephisto 是否出现问题")
        self.attempts = attempts_one_minute
        self.attempts.append(time.time())


proc_manager = ProcessManager()


class DaemonService(Service):
    id = "mephisto.daemon/core"

    @property
    def required(self):
        return set()

    @property
    def stages(self):  # type: ignore
        return {"preparing", "blocking", "cleanup"}

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            setup_token()
            logger.success("[MephistoDaemon] 已初始化 Daemon")

        async with self.stage("blocking"):
            while proc_manager.keep_alive and not manager.status.exiting:
                proc_manager.keep()
                await asyncio.sleep(1)

        async with self.stage("cleanup"):
            pass

        logger.success("[MephistoDaemon] 已退出 Daemon")


def launch_daemon(port: int):
    mgr = it(Launart)
    mgr.add_component(DaemonService())
    mgr.add_component(
        UvicornASGIService(
            "127.0.0.1",
            port or get_unoccupied_port(),
            {"": cast(ASGI3Application, fastapi)},
        )
    )
    mgr.add_component(FastAPIService(fastapi))
    mgr.launch_blocking()
