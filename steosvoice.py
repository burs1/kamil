"""
Steos voice api interactor
"""

import os
import httpx

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

    def synth(self, text):
        """ Sends request to make tts """

        body = {'voice_id': self.voice_id, 'text': text}

        try:
            response = httpx.post(
                self.base_url + 'tts',
                headers=self.headers,
                json=body
            ).json()
        except Exception as e:
            print("\n\n\n", e, "\n\n\n")
            return

        #print(response['audio_url'])

        if not response['status']:
            print(response['message'])
            return

        return response['audio_url']


    def save_audio(self, link, file_destionation = './voice-cache') -> None:
        """ Downloads audio from given link """

        if not os.path.isdir(file_destionation):
            os.mkdir(file_destionation)


