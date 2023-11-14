"""
External task generation module
"""
import os
import cfg
import random
import asyncio

from weather import get_weather
from datetime import datetime, timedelta
from numbers_to_words import num2text


def time_left_in_text(time:timedelta) -> str:
   hours = num2text(time.seconds//3600, ((u'час', u'час+а', u'часов'), 'm'))
   minutes = num2text(time.seconds%3600//60, ((u'минута', u'минуты', u'минут'), 'f'))
   seconds = num2text(time.seconds%60, ((u'секунда', u'секунды', u'секунд'), 'f'))
   milliseconds = num2text(time.microseconds//1000, ((u'миллисекунда', u'миллисекунды', u'миллисекунд'), 'f'))
   microseconds = num2text(time.microseconds%1000, ((u'микросекунда', u'микросекунды', u'микросекунд'), 'f'))

   return hours, minutes, seconds, milliseconds, microseconds




async def ping_random_user(thread) -> None:
    """ Mentions random user and deletes message in 3 seconds """
    users = [u for u in await thread.get_users() if not u.id in cfg.randping_whitelist and u.username]
    #print(users)

    if not users:
        thread.add_task(ping_random_user, datetime.now() + timedelta(seconds = 15), arguments=(thread,))
        return

    username = random.choice(users).username
    message = await thread.bot_instance.send_message(thread.chat_instance.id, f'@{username}')

    thread.add_task(ping_random_user, datetime.now() + timedelta(minutes = cfg.randping_interval), arguments=(thread,)) #cfg.randping_interval

    await asyncio.sleep(3)
    await message.delete()


async def send_weather_forecast(thread) -> None:
    """ Sends voice message with a weather forecast """
    RESP = {'cloudy': 'П+онебу облака распласт+ались.'}

    data = get_weather('novosibirsk')
    text = f'Русы одиннадцать одиннадцатого княжества, доброе утро. Сегодня в Свежесибирске за ставнями' + data["temp"][0] + f'градусов. {RESP[data["state"]]}.'.replace('-', 'минус')
    speech = thread.steos_instance.synth(text)

    await thread.bot_instance.sendVoice(thread.chat_instance.id, speech)

    thread.add_task(send_weather_forecast, datetime.now() + timedelta(hours=24), arguments=(thread,))


async def remind_about_shawarma(thread, time) -> None:
    """ Sends voice message with information about
    how much time is left before the shawarma """

    time_left = time - datetime.now()
    if datetime.now() > time:
        time += timedelta(days=7)
        text = 'Дружина, час шаурмы настал. ГОЙДА!'

        thread.add_task(remind_about_shawarma, time, arguments=(thread, time))
        speech = hread.steos_instance.save_audio(link = thread.steos_instance.synth(text))
        await thread.bot_instance.sendVoice(thread.chat_instance.id, speech)
        os.remove(speech)

        return


    hours = time_left.seconds//3600
    time_left = time_left_in_text(time_left)
    text = f'До похода ватаги в лавку Свиток осталось {time_left[0]}, {time_left[1]}, {time_left[2]}, {time_left[3]} и {time_left[4]}.'
    #print(text)
    speech = thread.steos_instance.save_audio(link = thread.steos_instance.synth(text))

    if not speech:
        return

    await thread.bot_instance.sendVoice(thread.chat_instance.id, speech)
    os.remove(speech)


    if hours < 13:
        new_time = time - timedelta(hours=1)
    else:
        new_time = datetime.now() + timedelta(hours=random.randint(1, 11), minutes=random.randint(0, 59))
    thread.add_task(remind_about_shawarma, new_time, arguments=(thread, time))

