from dataclasses import dataclass
from datetime import datetime
from typing import Final, Literal

from avilla.core import Selector

from mephisto.library.util.permission.query import query_permission_single_entry

WILDCARD_PERMISSION_SCOPE: Final[Literal["*"]] = "*"
WILDCARD_PERMISSION_TARGET: Final[Literal["*"]] = "*"
WILDCARD_SCENE: Final[Literal["*"]] = "*"
WILDCARD_CLIENT: Final[Literal["*"]] = "*"


@dataclass
class Permission:
    scope: str
    target: str
    effective: bool = True
    create_time: datetime | None = None
    expire_time: datetime | None = None

    def is_scope_wild(self):
        return self.scope == WILDCARD_PERMISSION_SCOPE

    def is_target_wild(self):
        return self.target == WILDCARD_PERMISSION_TARGET

    def __str__(self):
        return f"{self.scope}:{self.target}"

    def __repr__(self):
        if self.effective:
            return f"<Permission {self.scope}:{self.target} (Effective)>"
        return f"<Permission {self.scope}:{self.target}>"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __gt__(self, other):
        assert isinstance(other, Permission)

        if other.is_scope_wild():
            return False

    async def query(self, scene: Selector, client: Selector) -> "Permission":
        return await query_permission_single_entry(scene, client, self)
