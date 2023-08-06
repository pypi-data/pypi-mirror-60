"""Файл для управления запуском ботом."""
import time
import os
import sys
from signal import SIGTERM

from .bot_controll.chests_bot import Bot
from .bot_controll.args import namespace

bot = Bot(namespace.screen, namespace.chest, namespace.color)


def start_bot():
    if namespace.debug:
        bot.debug()
    else:
        if namespace.timer:
            # ToDo не проверил как работает для винды, возможно нужно будет переписать с вилки на мультипроцессы
            pid = os.fork()
            if pid == 0:
                # запускаем бота в дочке
                while True:
                    time.sleep(60)
                    bot.bot_execute()
            if pid > 0:
                # основой процесс слипаем на время указанное в таймере
                time.sleep(namespace.timer)
                # убийство дочернего процесса
                try:
                    os.kill(pid, SIGTERM)
                except OSError as e:
                    if "No such process" not in e.strerror or "Нет такого процесса" not in e.strerror:
                        sys.exit(1)
                    else:
                        print(e.strerror)
                        sys.exit(1)
        else:
            while True:
                time.sleep(60)
                bot.bot_execute()
