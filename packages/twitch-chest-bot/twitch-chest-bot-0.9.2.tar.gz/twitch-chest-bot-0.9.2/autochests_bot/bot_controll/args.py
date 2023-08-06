"""Файл содержит аргументы для управления запуском бота."""
import argparse

parser = argparse.ArgumentParser(description='Запуск бота для автоматического сбора сундуков на twitch.')
parser.add_argument(
    '--debug',
    default=False,
    help='При установке этого ключа, скрипт будет запущен в дебаг режиме.',
    action='store_true'
)

parser.add_argument(
    '--screen',
    default=(1500, 1000, 1760, 1100),
    type=int,
    nargs='+',
    help='Координаты внутри которых будет обрабатываться изображение. Передавать через пробел x1 y1 x2 y2'
)

parser.add_argument(
    '--chest',
    default=(1617, 1048),
    type=int,
    nargs='+',
    help='Координаты куда будет устанавливаться курсор для клика. Передавать через пробел x y'
)

parser.add_argument(
    '--color',
    default=(0, 230, 203),
    type=int,
    nargs='+',
    help='Искомый цвет на обрабатываемом участке экрана. Передавать в формате RGB через пробел'
)

parser.add_argument(
    '--timer',
    default=0,
    type=int,
    help='Время, на которое будет запущен бот'
)

namespace = parser.parse_args()
