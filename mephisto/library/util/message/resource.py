import hashlib
from pathlib import Path
from typing import TypeVar

import filetype
from avilla.core import Context, Resource
from avilla.core.builtins.capability import CoreCapability
from avilla.core.builtins.resource_fetch import CoreResourceFetchPerform
from avilla.core.resource import LocalFileResource, RawResource, UrlResource
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.selector import Selector
from avilla.standard.qq.elements import MarketFace
from graia.amnesia.message import Element, MessageChain
from loguru import logger

from mephisto.library.model.exception import AttachmentRecordNotFound
from mephisto.shared import DATA_ROOT


class RecordAttachmentResource(Resource[bytes]):
    @property
    def digest(self):
        return self.selector.pattern["digest"]


class RecordResourceFetchPerform((m := ApplicationCollector())._):
    m.namespace = "mephisto/core::resource"
    m.identify = "fetch"

    @m.entity(CoreCapability.fetch, resource=RecordAttachmentResource)
    async def fetch_attachment(self, resource: RecordAttachmentResource):
        if file := next(
            (
                DATA_ROOT / "attachment" / resource.digest[:2] / resource.digest[2:4]
            ).rglob(f"{resource.digest}*"),
            None,
        ):
            return file.read_bytes()
        raise AttachmentRecordNotFound(resource)


TR = TypeVar("TR", bound=Resource)


def extract_resources(message: MessageChain) -> list[tuple[int, Element, Resource]]:
    resources: list[tuple[int, Element, Resource]] = []
    for index, element in enumerate(message):
        if hasattr(element, "resource") and isinstance(element.resource, Resource):  # type: ignore
            resources.append((index, element, element.resource))  # type: ignore
    return resources


_translation: dict = {MarketFace: lambda _: UrlResource(_.url)}


async def save_resources(
    ctx: Context,
    message_chain: MessageChain,
    base_path: Path = DATA_ROOT / "attachment",
) -> list[Path | Exception]:
    results: list[Path | Exception] = []
    for element in message_chain:
        if type(element) in _translation:
            resource = _translation[type(element)](element)
            setattr(element, "resource", resource)
        elif not hasattr(element, "resource") or not isinstance(
            element.resource, Resource
        ):
            continue
        else:
            resource: Resource = element.resource  # type: ignore
        try:
            logger.debug(
                f"Fetching resource {type(resource)}({resource.to_selector().display})"
            )
            if isinstance(resource, LocalFileResource):
                raw = await CoreResourceFetchPerform(ctx.staff).fetch_localfile(
                    resource
                )
            elif isinstance(resource, RawResource):
                raw = await CoreResourceFetchPerform(ctx.staff).fetch_raw(resource)
            elif isinstance(resource, UrlResource):
                raw = await CoreResourceFetchPerform(ctx.staff).fetch_url(resource)
            else:
                raw = await ctx.fetch(resource)
            digest = hashlib.md5(raw).hexdigest()
            path = base_path / digest[:2] / digest[2:4] / digest
            path.parent.mkdir(parents=True, exist_ok=True)
            if ext := filetype.guess_extension(raw):
                path = path.with_suffix(f".{ext}")
            else:
                logger.warning("Cannot guess file type of resource")
            path.write_bytes(raw)
            logger.debug(f"Saved resource to {path}")
            results.append(path)
            setattr(
                element,
                "resource",
                RecordAttachmentResource(
                    Selector().land("mephisto-attachment").digest(digest)
                ),
            )
        except NotImplementedError as e:
            logger.error(
                f"Fetching resource {type(resource)}"
                f"({resource.to_selector().display}) is not supported"
            )
            results.append(e)
        except Exception as e:
            logger.error(f"Error fetching resource: {e}")
            results.append(e)
    return results
