import json
from http import HTTPStatus
from urllib.parse import unquote

import filetype
from avilla.core import Avilla, Context, Message
from avilla.standard.core.message import (
    MessageEdited,
    MessageReceived,
    MessageRevoked,
    MessageSent,
)
from creart import it
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from graia.broadcast import PropagationCancelled
from graia.saya.builtins.broadcast.shortcut import listen, priority
from graiax.fastapi.saya.route import get
from launart import Launart

from mephisto import __version__
from mephisto.library.service import DataService
from mephisto.library.service.module import ModuleStore
from mephisto.library.util.const import (
    MODULE_ASSET_ENDPOINT,
    TEMPORARY_FILE_ENDPOINT,
    TEMPORARY_FILES_ROOT,
)
from mephisto.library.util.message.resource import extract_resources, save_resources
from mephisto.library.util.message.serialize import serialize
from mephisto.library.util.orm.table import RecordTable
from mephisto.library.util.storage import fetch_file
from mephisto.shared import MEPHISTO_REPO, GenericErrorResponse, GenericSuccessResponse


@listen(MessageReceived)
@priority(1)
async def ignore_self_message(ctx: Context):
    if hash(ctx.client) == hash(ctx.self):
        raise PropagationCancelled()


@listen(MessageReceived, MessageSent)
@priority(-1)
async def record_received(avilla: Avilla, ctx: Context, message: Message):
    registry = avilla.launch_manager.get_component(DataService).registry
    engine = await registry.create(message.scene)
    await save_resources(ctx, message.content)
    resources = extract_resources(message.content)
    content = serialize(message.content)
    await engine.insert_or_update(
        RecordTable,
        RecordTable.message_id == message.id,
        message_id=message.id,
        scene=message.scene.display,
        client=message.sender.display,
        selector=message.to_selector().display,
        time=message.time,
        content=content,
        attachments=json.dumps(
            {k: v.to_selector().display for k, _, v in resources}, ensure_ascii=False
        ),
        reply_to=message.reply.display if message.reply else None,
    )


@listen(MessageEdited)
@priority(-1)
async def record_edited(avilla: Avilla, ctx: Context, message: Message):
    registry = avilla.launch_manager.get_component(DataService).registry
    engine = await registry.create(message.scene)
    await save_resources(ctx, message.content)
    resources = extract_resources(message.content)
    content = serialize(message.content)
    await engine.update(
        RecordTable,
        RecordTable.message_id == message.id,
        message_id=message.id,
        scene=message.scene.display,
        client=message.sender.display,
        selector=message.to_selector().display,
        time=message.time,
        content=content,
        attachments=json.dumps(
            {k: v.to_selector().display for k, _, v in resources}, ensure_ascii=False
        ),
        reply_to=message.reply.display if message.reply else None,
        edited=True,
        edit_time=message.time,
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
        if mime := filetype.guess_mime(file.read_bytes()):
            return FileResponse(file, filename=file.name, media_type=mime)
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
            if mime := filetype.guess_mime(file.read_bytes()):
                return FileResponse(file, filename=file.name, media_type=mime)
            return FileResponse(file, filename=file.name)
    raise HTTPException(
        HTTPStatus.NOT_FOUND,
        {"message": "File not found", "data": {"module": module, "asset": asset}},
    )
