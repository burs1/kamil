import httpx

class SteosVoice():
    voice_id = 1
    base_url = 'https://api.voice.steos.io/v1/get/'

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': api_key}

    def set_voice(self, name):
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
        body = {'voice_id': self.voice_id, 'text': text, 'format': 'mp3'}

        try:
            response = httpx.post(
                self.base_url + 'tts',
                headers=self.headers,
                json=body
            ).json()
        except Exception as e:
            print(e)
            return

        if not response['status']:
            print(response['message'])
            return

        return response['audio_url']

