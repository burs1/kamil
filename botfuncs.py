"""
External task generation module
"""

import cfg
import random
import asyncio

from weather import get_weather
from datetime import datetime, timedelta


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
    text = f'До похода ватаги в лавку Свиток осталось {time_left.seconds//3600} часов, {time_left.seconds%3600//60} минут, {time_left.seconds%3600} секунд, {time_left.microseconds//1000} милисекунд и {time_left.microseconds%1000} микросекунд.'
    speech = thread.steos_instance.synth(text)

    if not speech:
        return

    await thread.bot_instance.sendVoice(thread.chat_instance.id, speech, duration=10)

    if datetime.now() > time:
        time += timedelta(days=7)
        thread.add_task(remind_about_shawarma, time, arguments=(thread, time))
        return

    if time_left.seconds//3600 < 13:
        new_time = time - timedelta(hours=1)
    else:
        new_time = datetime.now() + timedelta(hours=random.randint(1, 11), minutes=random.randint(0, 59))
    thread.add_task(remind_about_shawarma, datetime.now() + timedelta(hours=24), arguments=(thread, time))

