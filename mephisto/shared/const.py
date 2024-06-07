from pathlib import Path
from typing import Final

MEPHISTO_ROOT: Final[Path] = Path(__file__).parent.parent.resolve()
PROJECT_ROOT: Final[Path] = MEPHISTO_ROOT.parent.resolve()
CONFIG_ROOT: Final[Path] = MEPHISTO_ROOT / "config"
DATA_ROOT: Final[Path] = MEPHISTO_ROOT / "data"
LOG_ROOT: Final[Path] = MEPHISTO_ROOT / "log"
