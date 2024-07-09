import os
from datetime import time
from pathlib import Path

import richuru
from loguru import logger
from rich.console import Console
from rich.theme import Theme


def setup_logger(sink: Path, log_rotate: int):
    level = "DEBUG" if os.environ["MEPHISTO_DEBUG"] == "1" else "INFO"
    level = "TRACE" if os.environ["MEPHISTO_TRACE"] == "1" else level
    if os.environ["MEPHISTO_NO_RICHURU"] == "1":
        logger.info("[Logger] Richuru disabled")
    else:
        richuru.install(
            rich_console=Console(
                theme=Theme(
                    {
                        "logging.level.success": "green",
                        "logging.level.debug": "magenta",
                        "logging.level.trace": "bright_black",
                    }
                )
            ),
            level=level,
        )
    logger.add(
        sink / "{time:YYYY-MM-DD}" / "common.log",
        level="INFO",
        retention=f"{log_rotate} days" if log_rotate else None,
        encoding="utf-8",
        rotation=time(),
    )
    logger.add(
        sink / "{time:YYYY-MM-DD}" / "error.log",
        level="ERROR",
        retention=f"{log_rotate} days" if log_rotate else None,
        encoding="utf-8",
        rotation=time(),
    )
