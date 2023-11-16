"""
Steos voice api interactor
"""

import os
import httpx

import urllib.request

class SteosVoice():
    voice_id = 1
    base_url = 'https://api.voice.steos.io/v1/get/'

    def __init__(self, api_key) -> None:
        self.api_key = api_key
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': api_key}

    def set_voice(self, name:str) -> None:
        """ Setup voice for message """

        try:
            response = httpx.get(
                self.base_url + 'voices',
                headers=self.headers
            ).json()
        except Exception as e:
            print(e)
            return

        if not response['status']:
            print(response['message'])
            return

        for voice in response['voices']:
            if voice['name']['RU'].startswith(name):
                self.voice_id = voice['voice_id']
                break
        else:
            print(f'Voice {name} is missing!')

    def synth(self, text:str):
        """ Sends request to make tts """

        body = {'voice_id': self.voice_id, 'text': text, 'format':'mp3'}

        try:
            response = httpx.post(
                self.base_url + 'tts',
                headers=self.headers,
                json=body
            ).json()
        except Exception as e:
            print("\n\n\n", e, "\n\n\n")
            return

        #print(response)

        if not response['status']:
            return

        return response['audio_url']


    def save_audio(self, link:str, file_destionation_dir:str = 'voice-cache') -> str:
        """ Downloads audio from given link and returns filepath"""

        if not os.path.isdir(file_destionation_dir):
            os.mkdir(file_destionation_dir)

        #print(link)

        file_path = file_destionation_dir + '/' + link.split('/')[-1]
        urllib.request.urlretrieve(link, file_path)

        return file_path


    def clear_cache(self, cache_dir:str = 'voice-cache'):
        """ Clears all cache of downloaded voices """

        for file in os.listdir(cache_dir):
            os.remove(f"{cache_dir}/{file}")

        os.rmdir(cache_dir)


