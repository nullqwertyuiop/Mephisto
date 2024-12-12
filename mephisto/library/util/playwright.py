from pathlib import Path
from typing import Final

import filetype
from loguru import logger
from playwright.async_api import Page, Route
from yarl import URL

from mephisto.shared import DATA_ROOT

ASSETS_DIR: Final[Path] = DATA_ROOT / "assets"
FONT_DIR: Final[Path] = ASSETS_DIR / "fonts"


async def route_fonts(page: Page, *font_type: str):
    font_type = font_type or ("woff", "woff2", "ttf", "otf")
    await page.route("**/*.{" + ",".join(font_type) + "}", fulfill_font)
    logger.debug(f"[Playwright] Routed font requests: {font_type}")


async def fulfill_font(route: Route):
    url = URL(route.request.url)
    filename = url.parts[-1]
    if not FONT_DIR.is_dir():
        FONT_DIR.mkdir(parents=True)
        await route.continue_()
        logger.debug(f"[Playwright] Continue font request: {filename}")
    elif font := next(FONT_DIR.rglob(filename), None):
        await route.fulfill(
            body=font.read_bytes(), content_type=filetype.guess_mime(font)
        )
        logger.debug(f"[Playwright] Fulfilled font request: {filename}")
    else:
        await route.continue_()
        logger.debug(f"[Playwright] Continue font request: {filename}")
