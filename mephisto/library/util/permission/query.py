from datetime import datetime
from typing import Literal

from avilla.core import Selector
from creart import it
from launart import Launart
from sqlalchemy import select

from mephisto.library.model.exception import PermissionEntryNotFound
from mephisto.library.service import DataService
from mephisto.library.util.orm.table import PermissionTable
from mephisto.library.util.permission.model import Permission


async def query_permission_single_entry(
    scene: Selector | Literal["*"],
    client: Selector | Literal["*"],
    permission: Permission,
) -> Permission:
    scope = permission.scope
    target = permission.target
    scene_str = scene.display if isinstance(scene, Selector) else scene
    client_str = client.display if isinstance(client, Selector) else client
    engine = await it(Launart).get_component(DataService).get_main_engine()
    async with engine.session() as session:
        result = await session.scalar(
            select(PermissionTable)
            .where(
                PermissionTable.scene == scene_str,
                PermissionTable.client == client_str,
                PermissionTable.scope == scope,
                PermissionTable.target == target,
                PermissionTable.expire_time > datetime.now(),
            )
            .order_by(PermissionTable.id.desc())
        )
        if not result:
            raise PermissionEntryNotFound(scene, client, f"{scope}:{target}")
        return Permission(
            scope=result.scope,  # type: ignore
            target=result.target,  # type: ignore
            effective=result.effective,  # type: ignore
            create_time=result.create_time,  # type: ignore
            expire_time=result.expire_time,  # type: ignore
        )


async def query_permission_single_selector(
    scene: Selector | Literal["*"],
    client: Selector | Literal["*"],
) -> list[Permission]:
    scene_str = scene.display if isinstance(scene, Selector) else scene
    client_str = client.display if isinstance(client, Selector) else client
    engine = await it(Launart).get_component(DataService).get_main_engine()
    async with engine.session() as session:
        result = await session.execute(
            select(PermissionTable).where(
                PermissionTable.scene == scene_str,
                PermissionTable.client == client_str,
                PermissionTable.expire_time > datetime.now(),
            )
        )
        return [
            Permission(
                scope=row.scope,  # type: ignore
                target=row.target,  # type: ignore
                effective=row.effective,  # type: ignore
                create_time=row.create_time,  # type: ignore
                expire_time=row.expire_time,  # type: ignore
            )
            for row in result.scalars()
        ]
