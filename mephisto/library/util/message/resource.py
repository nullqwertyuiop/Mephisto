from __future__ import annotations

import hashlib
from copy import deepcopy
from importlib.resources import Resource
from pathlib import Path
from typing import TypeVar

import filetype
from avilla.core import Context, Resource
from graia.amnesia.message import Element, MessageChain
from loguru import logger

from mephisto.shared import DATA_ROOT

from avilla.core.resource import LocalFileResource, RawResource, UrlResource
from avilla.core.ryanvk.collector.application import ApplicationCollector
from avilla.core.builtins.capability import CoreCapability


class RecordAttachmentResource(Resource[bytes]): ...


class RecordResourceFetchPerform((m := ApplicationCollector())._):
    @m.entity(CoreCapability.fetch, resource=RecordAttachmentResource)
    async def fetch_record(self, resource: RecordAttachmentResource):
        pass


TR = TypeVar("TR", bound=Resource)


def extract_resources(message: MessageChain) -> list[tuple[int, Element, Resource]]:
    resources: list[tuple[int, Element, Resource]] = []
    for index, element in enumerate(message):
        if hasattr(element, "resource") and isinstance(element.resource, Resource):  # type: ignore
            resources.append((index, element, element.resource))  # type: ignore
    return resources


def fix_multimedia_nt_qq(
    resource: TR,
) -> TR:
    original = "https://multimedia.nt.qq.com.cn"
    replaced = "http://multimedia.nt.qq.com.cn"  # noqa
    selector = deepcopy(resource.selector)
    selector = selector.modify(
        {k: v.replace(original, replaced) for k, v in selector.pattern.items()}
    )
    resource.selector = selector
    if hasattr(resource, "url"):
        resource.url = resource.url.replace(original, replaced)
    return resource


_preprocessors: dict = {
    lambda resource: "https://multimedia.nt.qq.com.cn"
    in resource.selector.display: fix_multimedia_nt_qq,
}


async def save_resources(
    ctx: Context, *resources: Resource, base_path: Path = DATA_ROOT / "attachment"
) -> list[Path | Exception]:
    results: list[Path | Exception] = []
    for resource in resources:
        try:
            for prep in _preprocessors:
                if prep(resource):
                    resource = _preprocessors[prep](resource)

            logger.debug(
                f"Fetching resource {type(resource)}({resource.to_selector().display})"
            )
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
