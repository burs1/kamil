#import utils
import asyncio
#import bot_functions as bf
#import questionnaire_functions as qf

from telegram import (
	KeyboardButton,
	KeyboardButtonPollType,
	Poll,
	ReplyKeyboardMarkup,
	ReplyKeyboardRemove,
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


# async def process_qf(user, data, update, context: ContextTypes.DEFAULT_TYPE, chat_id=None):
# 	global users_cache

# 	if users_cache[user]['status'] == 'finished':
# 		await context.bot.send_message(update.message.chat.id, 'Вы уже заполнили анкету, чтобы сделать это снова, введите /start')
# 		return

# 	in_rules = utils.in_rules(data, questions_sequence[users_cache[user]['status']]) # in_rules returns tuple
# 	if not in_rules[0]:
# 		await context.bot.send_message(update.message.chat.id, in_rules[1])
# 		return

# 	users_cache[user] = await qf.struct_info(user_data = users_cache[user], update=update,
# 														recieved_data=data, context=context, chat_id=chat_id)
# 	utils.dump_users_cache(users_cache)

# 	if users_cache[user]['status'] == 'finished':
# 		utils.save_result(data=users_cache[user])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user = update.message.from_user

	print(f'{user.first_name} {user.last_name} {user.username} [{user.id}]')
	#
	print(await context.bot.send_message(update.message.chat.id, 'test message'))
	#for i in range(100):
		#await update.message.reply_text(' '.join(["@" + i.user.username for i in await update.message.chat.get_administrators()]))
	#users_cache[user.id] = await qf.start(context=context, chat_id=update.message.chat.id)
	#users_cache[user.id]['id'] = user.id


# async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
# 	answer = update.poll_answer
# 	answered_poll = context.bot_data[answer.poll_id]

# 	try:
# 		questions = answered_poll["questions"]
# 		if answered_poll['allows_multiple_answers']:
# 			data = [questions[i] for i in answer.option_ids]
# 		else:
# 			data = questions[answer.option_ids[0]]
# 	except KeyError:
# 		return
# 	await process_qf(user=update.effective_user.id, data=data, update=update, context=context, chat_id=answered_poll["chat_id"])

# 	await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])
# 	utils.dump_users_cache(users_cache)


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