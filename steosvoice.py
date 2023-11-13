import httpx

class SteosVoice():
    voice_id = 1

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': api_key}

    def set_voice(self, name):
        self.voice_id = id
        response = httpx.get(
            'https://api.voice.steos.io/v1/get/voices',
            headers=self.headers
        ).json()

        for voice in response['voices']:
            if voice['name']['RU'].startswith(name):
                self.voice_id = voice['voice_id']
                break
        else:
            print(f'Name {name} is missing!')

    def synth(self, text):
        body = {'voice_id': self.voice_id, 'text': text, 'format': 'mp3'}

        response = httpx.post(
            'https://api.voice.steos.io/v1/get/tts',
            headers=self.headers,
            json=body
        ).json()

        if response['status']:
            return response['audio_url']
        return None
