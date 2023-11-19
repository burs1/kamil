"""
VK social media interactor
"""

import vk_api

from datetime import datetime
from cfg import VK_API_KEY, NO_WARMUP_KEYWORD, WARMUP_INFO_GROUP


class VkApi:
    def __init__(self, apikey:str = VK_API_KEY) -> None:
        self.session = vk_api.VkApi(token=apikey)
        self.vkapi = self.session.get_api()


    def get_posts(self, domain:str, count:int = 1, offset:int = 0):
        """ Returns n last posts from domain"""

        return self.vkapi.wall.get(domain=domain, count=count, offset=offset)['items']


def get_powermorning_sesc_status() -> int:
    """
    Returns if today 'powermorning_sesc' group posted about warming up
        or it was canceled

    Returns:
        0 - if no warmup
        1 - if warmup is gonna be
        2 - if there is no info yet about it
    """

    instance = VkApi()

    post = VkApi().get_posts(WARMUP_INFO_GROUP)[0]
    date = datetime.fromtimestamp(post['date'])

    if date.day < datetime.now().day:
        return 2

    return int(NO_WARMUP_KEYWORD not in post['text'])
