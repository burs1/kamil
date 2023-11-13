import openai
import tiktoken

class ChatGPT:
    chats = dict()

    def __init__(self, api_key, model='gpt-3.5-turbo', maxcost=4000):
        openai.api_key = api_key
        self.maxcost = maxcost
        self.model = model
        self.encoding = tiktoken.encoding_for_model(model)

    def ask(self, promt, simple=True):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {'role': 'user', 'content': promt}
                ]
            )
        except Exception as e:
            print(e)
            return ''

        if simple:
            return response['choices'][0]['message']['content']
        return response

    def ask_chat(self, name, promt, simple=True):
        chat = self.chats.setdefault(name, Chat(self.encoding, self.maxcost))
        chat.add_message('user', promt)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=chat.get_context()
            )
        except Exception as e:
            print(e)
            return ''

        chat.add_message(*response['choices'][0]['message'].items(), response['usage']['completion_tokens'])

        if simple:
            return response['choices'][0]['message']['content']
        return response

class Chat:
    messages = []
    costs = []

    def __init__(self, encoding, maxcost):
        self.encoding = encoding
        self.maxcost = maxcost

    def add_message(self, role, content, cost=-1):
        if cost < 0:
            cost = len(self.encoding.encode(content))

        self.messages.append( {'role': role, 'content': content} )
        self.costs.append(cost)

        while sum(self.costs) > self.maxcost:
            del self.messages[0]
            del self.costs[0]

    def get_context(self):
        return self.messages
