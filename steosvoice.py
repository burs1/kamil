"""
Steos voice api interactor
"""

import os
import httpx

import urllib.request

class SteosVoice():
    _voice_id = 1
    _base_url = 'https://api.voice.steos.io/v1/get/'

    def __init__(self, api_key) -> None:
        self.api_key = api_key
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': api_key}

    def __request(self, url, body:dict=None, tries:int=100) -> dict:
        response = None

        for _ in range(tries):
            try:
                if body:
                    response = httpx.post(self._base_url + url, headers=self.headers, json=body).json() 
                else:
                    response = httpx.get(self._base_url + url, headers=self.headers).json()
                break
            except Exception as e:
                print('\n\n\n', e, '\n\n\n')
 
        if not isinstance(response, dict) or 'status' not in response.keys():
            print('\n\n\nInvalid response form\n\n\n')
            return dict()

        if not response['status']:
            print('\n\n\n', response['message'], '\n\n\n')
            return dict()

        return response


    def set_voice(self, name:str) -> None:
        """ Setup voice for message """

        response = self.__request('voices')

        if not response:
            return

        for voice in response['voices']:
            if voice['name']['RU'].startswith(name):
                self.voice_id = voice['voice_id']
                break
        else:
            print(f'Voice {name} is missing!')

    def synth(self, text:str, mode:str) -> str:
        """ Sends request to make tts """

        if not mode in ['url', 'file']:
            raise ValueError(f'Mode {mode} doesn\'t exist')

        body = {'voice_id': self._voice_id, 'text': text, 'format':'mp3'}

        response = self.__request('tts', body=body)

        if not response:
            return ''

        if mode == 'url':
            return response['audio_url']
        return self.__save_audio(response['audio_url'])


    def __save_audio(self, link:str, file_destionation_dir:str = 'voice-cache') -> str:
        """ Downloads audio from given link and returns filepath"""

        if not os.path.isdir(file_destionation_dir):
            os.mkdir(file_destionation_dir)

        file_path = file_destionation_dir + '/' + link.split('/')[-1]
        urllib.request.urlretrieve(link, file_path)

        return file_path


    def clear_cache(self, cache_dir:str = 'voice-cache') -> None:
        """ Clears all cache of downloaded voices """

        if not os.path.isdir(cache_dir):
            return

        for file in os.listdir(cache_dir):
            os.remove(f"{cache_dir}/{file}")

        os.rmdir(cache_dir)


