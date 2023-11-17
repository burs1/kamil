#import utils
import cfg
import time
import random
import asyncio
import chatgpt
import botfuncs
import threading
import steosvoice

from datetime import datetime, timedelta

from telegram import (
	# KeyboardButton,
	# KeyboardButtonPollType,
	# Poll,
	# ReplyKeyboardMarkup,
	# ReplyKeyboardRemove,
	Update,
	User
)

from telegram.constants import ParseMode
#from constants import INTRO, questions_sequence
from telegram.ext import (
	Application,
	CommandHandler,
	ContextTypes,
	MessageHandler,
	#PollAnswerHandler,
	#PollHandler,
	filters,
)


__author__ = 'Yegor Yershov'


global users_cache
#users_cache = utils.load_users_cache() # {'user_id':data...}

bot_task_threads = {} # {'chat_id':TaskThread}



# class Task:
# 	def __init__(self, function:tuple, execution_timestamp:datetime) -> None:
# 		"""task with (function, args) and execution timestamp"""

# 		self.function = function[0]
# 		self.arguments = function[1]
# 		self.execution_timestamp = execution_timestamp

class clr:
    blue = '\033[94m'
    cyan = '\033[96m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    white = '\033[0m'
    bold = '\033[1m'

class TasksThread(threading.Thread):
    def __init__(self, bot_instance, chat_instance) -> None:
        """
        users_to_be_pinged - list of users to be randomly pinged
        interval - minutes per ping
        """

        self.task = None

		#self.ping_interval = ping_interval
        self.bot_instance = bot_instance
        self.chat_instance = chat_instance

        self.gpt_instance = chatgpt.ChatGPT(cfg.OPENAI_API_KEY)
        self.steos_instance = steosvoice.SteosVoice(cfg.STEOSVOICE_API_KEY)
        self.steos_instance.set_voice('Дрочеслав')
        
        self.tasks_list = []

        super().__init__(daemon=True)


    async def get_users(self) -> list[User]:
        """ Returns list with usernames of users"""
        return [admin.user for admin in await self.chat_instance.get_administrators()]


    def add_task(self, function, execution_timestamp:datetime, arguments:tuple=tuple()):
        """ Adds new task to the list """
        # send message in console
        print(f'{clr.yellow}New task added:{clr.white}')
        print(f'\tfunc:', function.__name__)
        if arguments:
            print(f'\targs:', arguments)
        print('\ttime:', execution_timestamp.strftime("%d.%m.%y %H:%M:%S"))

        self.tasks_list.append({'timestamp':execution_timestamp, 'function':function, 'args':arguments})


    async def setup_thread(self) -> None:
        while True:
            deletion_list = []
            for task in self.tasks_list:
                if datetime.now() >= task['timestamp']:
                    await task['function'](*task['args'])
                    deletion_list.append(task)

            for task in deletion_list:
                self.tasks_list.remove(task)


            time.sleep(1)


    async def send_voice_message(self, text:str) -> bool:
        """ Generates and sends voice message made from text """

        self.steos_instance.clear_cache()

        speech = self.steos_instance.save_audio(link = self.steos_instance.synth(text))

        if not speech:
            return False

        await self.bot_instance.sendVoice(self.chat_instance.id, speech)
        self.steos_instance.clear_cache()

        return True


    async def start_asyncio_task(self) -> None:
        self.task = asyncio.create_task(self.setup_thread())
        await self.task


    def stop_asyncio_task(self) -> None:
        self.task.cancel()
        self.join()


    def run(self) -> None:
        """Initting thread"""

        asyncio.run(self.start_asyncio_task())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user

    if update.message.chat.id not in bot_task_threads.keys():
        await update.message.delete()
        print(f'{clr.red}{user.username} [{user.id}]{clr.white} started bot polling')
        
        # create thread
        bot_task_threads[update.message.chat.id] = TasksThread(bot_instance = context.bot, chat_instance = update.message.chat)
        thread = bot_task_threads[update.message.chat.id]


		#bot_task_threads[update.message.chat.id].start()
		
		# add tasks
        thread.add_task(botfuncs.ping_random_user, datetime.now(), arguments=(thread,))
        thread.add_task(botfuncs.remind_about_shawarma, datetime.now(), arguments=(thread, botfuncs.generate_next_shawerma_time()))
        thread.add_task(botfuncs.send_weather_forecast, botfuncs.generate_next_weather_notification_time(), arguments=(thread,))

        await thread.setup_thread()

	#msg = await update.message.reply_text('hello')
	#for i in range(100):
		#await update.message.reply_text(' '.join(["@" + i.user.username for i in update.message.chat.get_administrators()]))
	#users_cache[user.id] = await qf.start(context=context, chat_id=update.message.chat.id)
	#users_cache[user.id]['id'] = user.id


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	#global users_cache
	print('new_message')
	user = update.message.from_user.id

	await context.bot.send_message(update.message.chat.id, 'test message')


# Main 
def main():
    print(f'{clr.green}Starting bot...')
    
    application = Application.builder().token(cfg.BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    #application.add_handler(MessageHandler(filters.TEXT, handle_message))
	#application.add_handler(PollAnswerHandler(receive_poll_answer))
	
    print(f'{clr.cyan}Bot is online')
    
    application.run_polling()

if __name__ == '__main__':
	main()
