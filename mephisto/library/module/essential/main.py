import hashlib
import json
from http import HTTPStatus
from urllib.parse import unquote

from avilla.core import Context, Message, Avilla, Resource, Selector
from avilla.standard.core.message import (
    MessageReceived,
    MessageSent,
    MessageEdited,
    MessageRevoked,
)
from creart import it
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from graia.amnesia.message import MessageChain, Text
from graia.broadcast import PropagationCancelled
from graia.saya.builtins.broadcast.shortcut import listen, priority
from graiax.fastapi.saya.route import get
from launart import Launart

from mephisto import __version__
from mephisto.library.module.essential._model import Attachment
from mephisto.library.service import DataService
from mephisto.library.service.module import ModuleStore
from mephisto.library.util.const import (
    TEMPORARY_FILE_ENDPOINT,
    MODULE_ASSET_ENDPOINT,
    TEMPORARY_FILES_ROOT,
)
from mephisto.library.util.message.serialize import serialize
from mephisto.library.util.orm.table import RecordTable, AttachmentTable
from mephisto.library.util.storage import fetch_file
from mephisto.shared import (
    DATA_ROOT,
    GenericSuccessResponse,
    MEPHISTO_REPO,
    GenericErrorResponse,
)


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
    return serialize(message), resources


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
        if await main_engine.scalar_eager(
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
        if await main_engine.scalar_eager(
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


@get("/core/service/version")
async def fastapi_version():
    commit = MEPHISTO_REPO.head.commit
    return GenericSuccessResponse(
        message=__version__,
        data={
            "version": __version__,
            "commit": {
                "sha": commit.hexsha,
                "message": commit.message,
                "time": commit.authored_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            },
        },
    )


@get(TEMPORARY_FILE_ENDPOINT)
async def fastapi_temp_file(id: str):
    if file := fetch_file(id, scope=TEMPORARY_FILES_ROOT):
        return FileResponse(file, filename=file.name)
    raise HTTPException(
        HTTPStatus.NOT_FOUND,
        GenericErrorResponse(
            code=HTTPStatus.NOT_FOUND, message="File not found", data={"id": id}
        ),
    )


@get(MODULE_ASSET_ENDPOINT)
async def fastapi_module_asset(module: str, asset: str):
    if metadata := it(Launart).get_interface(ModuleStore).get(module):
        if file := fetch_file(*unquote(asset).split("/"), scope=metadata.assets):
            return FileResponse(file, filename=file.name)
    raise HTTPException(
        HTTPStatus.NOT_FOUND,
        {"message": "File not found", "data": {"module": module, "asset": asset}},
    )
