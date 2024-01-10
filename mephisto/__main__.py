import os
from pathlib import Path

import toml
from loguru import logger

from mephisto.shared import MEPHISTO_ROOT, PROJECT_ROOT, setup_logger


def _init():
    parent_pyproject = Path(PROJECT_ROOT / "pyproject.toml")
    child_pyproject = Path(MEPHISTO_ROOT / "pyproject.toml")
    parent_pdm_lock = Path(PROJECT_ROOT / "pdm.lock")
    child_pdm_lock = Path(MEPHISTO_ROOT / "pdm.lock")
    child_pyproject.write_text(parent_pyproject.read_text())
    child_pdm_lock.write_text(parent_pdm_lock.read_text())


def _update_pyproject():
    parent_data = toml.loads(Path(PROJECT_ROOT / "pyproject.toml").read_text())
    child_data = toml.loads((MEPHISTO_ROOT / "pyproject.toml").read_text())
    parent_data["project"]["optional-dependencies"]["mephisto"] = child_data["project"][
        "optional-dependencies"
    ].get("mephisto", [])
    (MEPHISTO_ROOT / "pyproject.toml").write_text(toml.dumps(parent_data))


def _ensure_env():
    if not (MEPHISTO_ROOT / "pdm.lock").exists():
        logger.debug("PDM 锁文件不存在，正在安装依赖")
        os.system("pdm install")


def _ensure_daemon():
    env = os.environ
    if env.get("MEPHISTO_DAEMON") != "1":
        logger.critical("Mephisto 非守护进程启动，可能会导致 Mephisto 无法正常运行")
        return
    if env.get("MEPHISTO_DAEMON_TOKEN") is None:
        logger.critical("Mephisto 守护进程启动，但未提供合法的 TOKEN")
        return
    os.environ |= {"PDM_NO_SELF": "1"}
    logger.debug("Mephisto 由守护进程启动，token 为 {token}", token=env["MEPHISTO_DAEMON_TOKEN"])


def run():
    setup_logger(MEPHISTO_ROOT / "log", 7)
    _ensure_daemon()

    if (MEPHISTO_ROOT / "pyproject.toml").is_file():
        _init()

    _update_pyproject()
    _ensure_env()

    from mephisto.library import launch

    logger.info("Launching Mephisto...")
    launch()


if __name__ == "__main__":
    run()
