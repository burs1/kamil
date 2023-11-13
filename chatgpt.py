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
        responce = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {'role': 'user', 'content': promt}
            ]
        )

        if simple:
            return responce['choices'][0]['message']['content']
        return responce

    def ask_chat(self, name, promt, simple=True):
        chat = self.chats.setdefault(name, Chat(self.encoding, self.maxcost))
        chat.add_message('user', promt)
        
        responce = self.ask(promt, simple=False)

        chat.add_message(*responce['choices'][0]['message'].items(), responce['completion_tokens'])

        if simple:
            return responce['choices'][0]['message']['content']
        return responce

class Chat:
    messages = []
    costs = []

    def __init__(self, encoding, maxcost):
        self.encoding = encoding
        self.maxcost = maxcost

    def add_message(self, role, content, cost=-1):
        if cost < 0:
            cost = len(self.encoding.encode(content))

        self.messages.append( {"role": role, "content": content} )
        self.costs.append(cost)

        while sum(self.costs) > self.maxcost:
            del self.messages[0]
            del self.costs[0]

    def get_context(self):
        return self.messages
