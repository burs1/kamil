"""
External task generation module
"""
import os
import random
import vkfuncs
import asyncio

from weather import get_weather
from numbers_to_words import num2text
from datetime import datetime, timedelta
from cfg import RANDPING_INTERVAL, RANDPING_WHITELIST, SHAVERMA_SCHEDULE,\
                WEATHER_NOTIFICATION_TIME, WARMUP_NOTIFICATION_TIME


def time_left_in_text(time:timedelta) -> str:
    """ Formats timedelta into text """

    days = num2text(time.days, ((u'день', u'дня', u'дней'), 'm'))
    hours = num2text(time.seconds//3600, ((u'час', u'час+а', u'часов'), 'm'))
    minutes = num2text(time.seconds%3600//60, ((u'минута', u'минуты', u'минут'), 'f'))
    seconds = num2text(time.seconds%60, ((u'секунда', u'секунды', u'секунд'), 'f'))
    milliseconds = num2text(time.microseconds//1000, ((u'миллисекунда', u'миллисекунды', u'миллисекунд'), 'f'))
    microseconds = num2text(time.microseconds%1000, ((u'микросекунда', u'микросекунды', u'микросекунд'), 'f'))

    return hours, minutes, seconds, milliseconds, microseconds, days


async def ping_random_user(thread) -> None:
    """ Mentions random user and deletes message in 3 seconds """
    users = [u for u in await thread.get_users() if not u.id in RANDPING_WHITELIST and u.username]
    #print(users)

    if not users:
        print('There is no users to be pinged')
        thread.add_task(ping_random_user, datetime.now() + timedelta(seconds = 15), arguments=(thread,))
        return

    username = random.choice(users).username
    message = await thread.send_text_message(f'@{username}')

    thread.add_task(ping_random_user, datetime.now() + timedelta(minutes = RANDPING_INTERVAL), arguments=(thread,))

    await asyncio.sleep(3)
    await message.delete()


async def send_weather_forecast(thread) -> None:
    """ Sends voice message with a weather forecast """
    RESP = {'cloudy': 'П+онебу облака распласт+ались.'}

    data = get_weather('novosibirsk')
    text = u'Русы одиннадцать одиннадцатого княжества, доброе утро. Сегодня в Свежесибирске за ставнями ' + num2text(int(float(data['temp'])), ((u'градус', u'градуса', u'градусов'), 'm')) #  {RESP[data["state"]]}.
    await thread.send_voice_message(text = text)

    thread.add_task(send_weather_forecast, generate_next_notification_time(WEATHER_NOTIFICATION_TIME), arguments=(thread,))


async def remind_about_shawarma(thread, time) -> None:
    """ Sends voice message with information about
    how much time is left before the shawarma """

    time_left = time - datetime.now()
    if datetime.now() > time:
        time = generate_next_shawerma_time()
        text = 'Дружина, час шаурмы настал. ГОЙДА!'

        thread.add_task(remind_about_shawarma, time, arguments=(thread, time))
        await thread.send_voice_message(text = text)

        return


    hours = time_left.seconds//3600
    time_left = time_left_in_text(time_left)
    text = f'До похода ватаги в лавку Свиток осталось {time_left[5]}, {time_left[0]}, {time_left[1]}, {time_left[2]}, {time_left[3]} и {time_left[4]}.'

    await thread.send_voice_message(text = text)

    if hours < 13:
        new_reminder_time = time - timedelta(hours=1)
    else:
        new_reminder_time = datetime.now() + timedelta(hours=random.randint(1, 11), minutes=random.randint(0, 59))
    thread.add_task(remind_about_shawarma, new_reminder_time, arguments=(thread, time))


async def notify_about_warmup(thread):
    """
    Waits for information about morning warmup
    """


    res = vkfuncs.get_powermorning_sesc_status()
    if res == 2:
        thread.add_task(notify_about_warmup, datetime.now() + timedelta(minutes = 1), arguments = (thread))
        return
    elif res == 1:
        await thread.send_text_message(u'Дружина, объявляю обязательный утренний сбор на мероприятие зарядка!')
    else:
        await thread.send_text_message(u'Дружина, объявляю, что утренний сбор на зарядку не состоится.')

    thread.add_task(notify_about_warmup, generate_next_notification_time(WARMUP_NOTIFICATION_TIME), arguments = (thread))


def generate_next_shawerma_time():
    """ Gives closest shawerma visiting date in datetime.datetime format"""

    now = datetime.now()

    result_time = None
    for weekday in SHAVERMA_SCHEDULE:
        if weekday >= now.weekday():
            result_time = datetime(now.year, now.month, now.day + (weekday - now.weekday()),
                                                         SHAVERMA_SCHEDULE[weekday]['hour'],
                                                         SHAVERMA_SCHEDULE[weekday]['minute'],
                                                         SHAVERMA_SCHEDULE[weekday]['second'])

    if result_time is None:
        weekday = min(SHAVERMA_SCHEDULE.keys())
        result_time = datetime(now.year, now.month, now.day + 7 - (now.weekday() - weekday),
                                                         SHAVERMA_SCHEDULE[weekday]['hour'],
                                                         SHAVERMA_SCHEDULE[weekday]['minute'],
                                                         SHAVERMA_SCHEDULE[weekday]['second'])

    return result_time


def generate_next_notification_time(pattern:dict) -> datetime:
    """ Gives next weather notification moment datetime.datetime format"""

    now = datetime.now()
    target_datetime = datetime(year = now.year, month=now.month, day=now.day,
                                **pattern)

    return datetime(now.year, now.month, now.day + (now > target_datetime),
                    **pattern)
