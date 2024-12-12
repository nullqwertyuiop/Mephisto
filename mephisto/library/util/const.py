from pathlib import Path
from typing import Final

from mephisto.shared import DATA_ROOT

TEMPORARY_FILES_ROOT: Final[Path] = DATA_ROOT / "temp"
FILES_STORAGE_ROOT: Final[Path] = DATA_ROOT / "files"

TEMPORARY_FILE_ENDPOINT: Final[str] = "/core/service/temp"
MODULE_ASSET_ENDPOINT: Final[str] = "/core/service/module/asset"
MODULE_README_ENDPOINT: Final[str] = "/core/service/module/readme"
