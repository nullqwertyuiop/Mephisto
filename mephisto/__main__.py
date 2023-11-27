import os
from pathlib import Path

import toml
from loguru import logger

from mephisto.shared import MEPHISTO_ROOT, PROJECT_ROOT, setup_logger


def _update_pyproject():
    parent = toml.loads(Path(PROJECT_ROOT / "pyproject.toml").read_text())
    child = toml.loads((MEPHISTO_ROOT / "pyproject.toml").read_text())
    parent["project"]["optional-dependencies"]["mephisto"] = child["project"][
        "optional-dependencies"
    ]["mephisto"]
    del parent["project"]["readme"]
    del parent["project"]["license"]
    (MEPHISTO_ROOT / "pyproject.toml").write_text(toml.dumps(parent))


def _ensure_env():
    pdm_lock = Path(MEPHISTO_ROOT, "pdm.lock")
    if not pdm_lock.exists():
        os.system("pdm install")


def _ensure_daemon():
    env = os.environ
    if env.get("MEPHISTO_DAEMON") != "1":
        logger.critical("Mephisto 非守护进程启动，可能会导致 Mephisto 无法正常运行")
        return
    if env.get("MEPHISTO_DAEMON_TOKEN") is None:
        logger.critical("Mephisto 守护进程启动，但未提供合法的 TOKEN")
        return
    os.environ = os.environ | {"PDM_IGNORE_SAVED_PYTHON": "1", "PDM_NO_SELF": "1"}
    logger.debug("Mephisto 由守护进程启动，token 为 {token}", token=env["MEPHISTO_DAEMON_TOKEN"])


if __name__ == "__main__":
    setup_logger(MEPHISTO_ROOT / "log", 7)
    _ensure_daemon()
    _update_pyproject()
    _ensure_env()

    from mephisto.library.core import launch

    logger.info("Launching Mephisto...")
    launch()
