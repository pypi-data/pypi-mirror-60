"""Utilities to scrape search results from Google Images."""
import asyncio
import json
import logging
from typing import List

import aiohttp
import bs4

from . import utils


GOOGLE_SEARCH_ENDPOINT = "https://www.google.com/search"
LOG = logging.getLogger(__name__)


async def search_worker(
    index: int,
    session: aiohttp.ClientSession,
    search_queue: asyncio.Queue,
    download_queue: asyncio.Queue,
) -> None:
    worker_name = ".".join([__name__, "search_worker", str(index)])
    logger = logging.getLogger(worker_name)
    while True:
        query = await search_queue.get()
        logger.debug(f"read query '{query.query}'")
        params = (
            ("as_st", "y"),
            ("tbm", "isch"),
            ("hl", "en"),
            ("as_q", query.query),
            ("as_epq", ""),
            ("as_oq", ""),
            ("as_eq", ""),
            ("cr", ""),
            ("as_sitesearch", ""),
            ("safe", "images"),
            ("tbs", "itp:face" if query.face else "itp:photo"),
        )
        try:
            logger.debug(f"querying google for '{query.query}'")
            async with session.get(
                GOOGLE_SEARCH_ENDPOINT, params=params
            ) as response:
                logger.debug("fetched url %s", response.url)
                response_text = await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            logger.error(
                "could not query google images for %s (%s)",
                query.query,
                str(err),
            )
            response_text = ""
        logger.debug(f"done querying google for '{query}', parsing")
        found_images = parse_google_images_results(response_text, query)
        logger.info(
            "found %d images querying for %s", len(found_images), query
        )
        for image_metadata in found_images:
            # logger.debug("putting %s onto download queue", result.url)
            await download_queue.put(image_metadata)
        logger.debug(f"done parsing results for query '{query}'")
        search_queue.task_done()


def parse_google_images_results(
    html: str, query: utils.GoogleImagesQuery
) -> List[utils.ImageMetadata]:
    LOG.debug("parsing Google Images results")
    dom = bs4.BeautifulSoup(html, "html.parser")
    results = []
    for result_div in dom.select("div.rg_meta.notranslate"):
        results.append(parse_google_images_result(result_div.text, query))
    return results


def parse_google_images_result(
    result_text: str, query: utils.GoogleImagesQuery
) -> utils.ImageMetadata:
    metadata = json.loads(result_text)
    return utils.ImageMetadata(
        url=metadata["ou"],
        image_format=metadata["ity"],
        description=metadata["pt"],
        height=metadata["oh"],
        width=metadata["ow"],
        host=metadata["rh"],
        source=metadata["ru"],
        query=query,
    )
