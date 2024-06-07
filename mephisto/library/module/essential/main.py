import hashlib
import json

from avilla.core import Context, Message, Avilla, Resource, Selector
from avilla.standard.core.message import (
    MessageReceived,
    MessageSent,
    MessageEdited,
    MessageRevoked,
)
from graia.amnesia.message import MessageChain, Text
from graia.broadcast import PropagationCancelled
from graia.saya.builtins.broadcast.shortcut import listen, priority

from mephisto.library.module.essential._model import Attachment
from mephisto.library.service import DataService
from mephisto.library.util.orm.table import RecordTable, AttachmentTable
from mephisto.shared import DATA_ROOT


@listen(MessageReceived)
@priority(1)
async def ignore_self_message(ctx: Context):
    if hash(ctx.client) == hash(ctx.self):
        raise PropagationCancelled()


def quote_message(message: MessageChain) -> tuple[str, list[tuple[Resource, Selector]]]:
    resources: list[tuple[Resource, Selector]] = []
    for element in message:
        if hasattr(element, "resource") and isinstance(element.resource, Resource):  # type: ignore
            resources.append((element.resource, element.resource.to_selector()))  # type: ignore
        elif isinstance(element, Text):
            element.text.replace("[", "\\[")
    return repr(message), resources


async def dump_attachment(ctx: Context, resource: Resource) -> str:
    attachment = Attachment(ctx, resource)
    dumped_attachment = json.dumps(attachment.__dict__).encode()
    md5 = hashlib.md5(dumped_attachment).hexdigest()
    path = DATA_ROOT / "attachment" / md5[:2] / md5[2:4] / f"{md5}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(dumped_attachment)
    return path.relative_to(DATA_ROOT).as_posix()


@listen(MessageReceived, MessageSent)
@priority(-1)
async def record_received(avilla: Avilla, ctx: Context, message: Message):
    registry = avilla.launch_manager.get_component(DataService).registry
    main_engine = await registry.create("main")
    engine = await registry.create(message.scene)
    content, resources = quote_message(message.content)
    await engine.insert_or_update(
        RecordTable,
        RecordTable.message_id == message.id,
        message_id=message.id,
        scene=message.scene.display,
        client=message.sender.display,
        selector=message.to_selector().display,
        time=message.time,
        content=content,
        attachments=",".join(resource.display for (_, resource) in resources),
        reply_to=message.reply.display if message.reply else None,
    )

    for resource, selector in resources:
        if await main_engine.scalar(
            AttachmentTable, AttachmentTable.pattern == selector.display
        ):
            continue
        dumped = await dump_attachment(ctx, resource)
        await main_engine.insert_or_update(
            AttachmentTable,
            AttachmentTable.pattern == selector.display,
            pattern=selector.display,
            file_path=dumped,
        )


@listen(MessageEdited)
@priority(-1)
async def record_edited(avilla: Avilla, ctx: Context, message: Message):
    registry = avilla.launch_manager.get_component(DataService).registry
    main_engine = await registry.create("main")
    engine = await registry.create(message.scene)
    content, resources = quote_message(message.content)
    await engine.update(
        RecordTable,
        RecordTable.message_id == message.id,
        message_id=message.id,
        scene=message.scene.display,
        client=message.sender.display,
        selector=message.to_selector().display,
        time=message.time,
        content=content,
        attachments=",".join(resource.display for (_, resource) in resources),
        reply_to=message.reply.display if message.reply else None,
        edited=True,
        edit_time=message.time,
    )

    for resource, selector in resources:
        if await main_engine.scalar(
            AttachmentTable, AttachmentTable.pattern == selector.display
        ):
            continue
        dumped = await dump_attachment(ctx, resource)
        await main_engine.insert_or_update(
            AttachmentTable,
            AttachmentTable.pattern == selector.display,
            pattern=selector.display,
            file_path=dumped,
        )


@listen(MessageRevoked)
@priority(-1)
async def record_revoked(avilla: Avilla, ctx: Context, event: MessageRevoked):
    registry = avilla.launch_manager.get_component(DataService).registry
    engine = await registry.create(ctx.scene)
    await engine.insert_or_update(
        RecordTable,
        RecordTable.selector == event.message.to_selector().display,
        message_id=event.message.to_selector().last_value,
        scene=ctx.scene.display,
        client=event.sender.display if event.sender else None,
        selector=event.message.to_selector().display,
        deleted=True,
        delete_time=event.time,
    )
