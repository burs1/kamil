#import utils
import time
import random
import asyncio
import threading

from datetime import datetime, timedelta

from telegram import (
	# KeyboardButton,
	# KeyboardButtonPollType,
	# Poll,
	# ReplyKeyboardMarkup,
	# ReplyKeyboardRemove,
	Update,
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


global TOKEN, users_cache
TOKEN = '6940898113:AAGo5AmBgkRbK7-t_8pyZWMZg5NKnj_05rE'
#users_cache = utils.load_users_cache() # {'user_id':data...}



bot_task_threads = {} # {'chat_id':TaskThread}



# class Task:
# 	def __init__(self, function:tuple, execution_timestamp:datetime) -> None:
# 		"""task with (function, args) and execution timestamp"""

# 		self.function = function[0]
# 		self.arguments = function[1]
# 		self.execution_timestamp = execution_timestamp



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

		self.users_to_be_pinged = None

		self.tasks_list = []

		super().__init__(daemon=True)


	async def gen_pinging_users(self) -> list[str]:
		""" Returns list with usernames of pinging users"""
		PING_WHITELIST = [6940898113, 1378906881, 951065997]

		res = [admin.user.username for admin in await self.chat_instance.get_administrators() if (admin.user.id not in PING_WHITELIST and admin.user.username is not None)]
		return res


	def add_task(self, function, args:tuple, execution_timestamp:datetime):
		""" Adds new task to the list """
		self.tasks_list.append({'timestamp':execution_timestamp, 'function':function, "args":args})


	async def setup_thread(self) -> None:
		self.users_to_be_pinged = await self.gen_pinging_users()
		self.add_task(self.ping_random_user, tuple(), datetime.now())


		while True:
			deletion_list = []
			#print(self.tasks_list)
			for task in self.tasks_list:
				if datetime.now() >= task['timestamp']:
					await task['function'](*task['args'])
					deletion_list.append(task)

			for task in deletion_list:
				self.tasks_list.remove(task)


			time.sleep(1)


	async def start_asyncio_task(self) -> None:
		self.task = asyncio.create_task(self.setup_thread())
		await self.task


	def stop_asyncio_task(self) -> None:
		self.task.cancel()
		self.join()


	def run(self):
		"""Initting thread"""

		asyncio.run(self.start_asyncio_task())


	async def ping_random_user(self):
		""" Mentions random user and deletes message in 3 seconds """
		PING_INTERVAL = 30 # minutes
		print(self.users_to_be_pinged)
		self.users_to_be_pinged = await self.gen_pinging_users()
		message = await self.bot_instance.send_message(self.chat_instance.id, f'@{random.choice(self.users_to_be_pinged)}')

		self.add_task(self.ping_random_user, tuple(), datetime.now() + timedelta(minutes = PING_INTERVAL))
		print(self.tasks_list[-1])

		await asyncio.sleep(3)
		await message.delete()



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user = update.message.from_user

	print(f'{user.first_name} {user.last_name} {user.username} [{user.id}]')

	if update.message.chat.id not in bot_task_threads.keys():
		bot_task_threads[update.message.chat.id] = TasksThread(bot_instance = context.bot, chat_instance = update.message.chat)
		#bot_task_threads[update.message.chat.id].start()
		await bot_task_threads[update.message.chat.id].setup_thread()

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



def main():
	global TOKEN

	application = Application.builder().token(TOKEN).build()
	application.add_handler(CommandHandler("start", start))
	application.add_handler(MessageHandler(filters.TEXT, handle_message))
	#application.add_handler(PollAnswerHandler(receive_poll_answer))
	application.run_polling()

if __name__ == '__main__':
	main()