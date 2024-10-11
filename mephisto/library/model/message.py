from dataclasses import dataclass
from datetime import datetime
from typing import Self

from avilla.core import Selector
from creart import it
from graia.amnesia.message.chain import MessageChain
from launart import Launart

from mephisto.library.model.exception import MessageRecordNotFound
from mephisto.library.service import DataService
from mephisto.library.util.message.deserialize import deserialize
from mephisto.library.util.orm.table import RecordTable


@dataclass
class RebuiltMessage:
    scene: Selector
    client: Selector
    selector: Selector
    time: datetime
    content: MessageChain
    reply_to: Selector | None

    @classmethod
    async def from_selector(cls, selector: Selector, scene: Selector) -> Self:
        registry = it(Launart).get_component(DataService).registry
        engine = await registry.create(scene)
        async with engine.scalar(
            RecordTable, RecordTable.selector == selector.display
        ) as result:
            if not result:
                raise MessageRecordNotFound(selector, scene)

            return cls(
                scene=Selector.from_follows(str(result.scene)),
                client=Selector.from_follows(str(result.client)),  # type: ignore
                selector=Selector.from_follows(str(result.selector)),
                time=result.time,  # type: ignore
                content=deserialize(result.content),  # type: ignore
                reply_to=(
                    Selector.from_follows(str(result.reply_to))
                    if result.reply_to  # type: ignore
                    else None
                ),
            )
