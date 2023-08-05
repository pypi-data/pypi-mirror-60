import aiohttp
import asyncio
import logging

from functools import partial
from itertools import chain

from .TaskIterator import TaskIterator


class ReviewsLoader(object):
    REVIEWS_URL = "https://amp-api.apps.apple.com/v1/catalog/ru/apps/{app_id}/reviews?l=ru&offset={offset}&platform=web&additionalPlatforms=appletv,ipad,iphone,mac"
    REVIEWS_INFO_URL = "https://amp-api.apps.apple.com/v1/catalog/RU/apps/{app_id}?platform=web&additionalPlatforms=appletv%2Cipad%2Ciphone%2Cmac&extend=description%2CdeveloperInfo%2CeditorialVideo%2Ceula%2CfileSizeByDevice%2CmessagesScreenshots%2CprivacyPolicyUrl%2CprivacyPolicyText%2CpromotionalText%2CscreenshotsByType%2CsupportURLForLanguage%2CversionHistory%2CvideoPreviewsByType%2CwebsiteUrl&include=genres%2Cdeveloper%2Creviews%2Cmerchandised-in-apps%2Ccustomers-also-bought-apps%2Cdeveloper-other-apps%2Capp-bundles%2Ctop-in-apps%2Ceula&l=ru-ru"
    STEP_SIZE = 10
    
    def __init__(self, loop, app_id, token, timeout=10):
        self.loop = loop
        self.app_id = app_id
        self.token = token
        self.headers = headers={"Authorization": "Bearer {token}".format(token=token)}
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.reviews_url = partial(self.REVIEWS_URL.format, app_id=app_id)
        self.reviews_info_url = self.REVIEWS_INFO_URL.format(app_id=app_id)
    
    async def get_reviews(self, offset, complete_callback, backlog_callback):
        try:
            async with aiohttp.ClientSession(loop=self.loop, timeout=self.timeout, headers=self.headers) as session:
                async with session.get(self.reviews_url(offset=offset)) as response:
                    if response.status == 404:
                        complete_callback()
                        return list()
                    return (await response.json())["data"]
        except Exception as e:
            backlog_callback(offset)
            logging.warning("Error on offset={offset}: {error}".format(offset=offset, error=str(e)))
            return list()

    async def get(self, batch_size=2000, requests_interval=0.3):
        for tasks in TaskIterator(self.get_reviews, batch_size=batch_size):
            reviews = list(chain.from_iterable(await asyncio.gather(*tasks)))
            for review in reviews:
                yield review
            await asyncio.sleep(requests_interval)
        