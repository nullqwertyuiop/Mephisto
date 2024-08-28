from typing import Final

from git import Repo

from .const import PROJECT_ROOT

MEPHISTO_REPO: Final[Repo] = Repo(PROJECT_ROOT)
