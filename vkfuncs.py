import vk_api
import cfg

class VkApi:
    def __init__(self, apikey):
        self.session = vk_api.VkApi(token=cfg.vk_api_key)
        self.vkapi = self.session.get_api()

    def get_posts(self, domain, count=1, offset=0):
        return self.vkapi.wall.get(domain=domain, count=count, offset=offset)['items']
