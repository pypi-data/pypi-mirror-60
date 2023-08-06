"""Файл с основным классом бота, отвечающим за работу бота."""
import time

import numpy as np
import pyscreenshot as sc
from pynput.mouse import Button as MButton, Controller as MController


class Bot:
    def __init__(self, screen, chest, color):
        self.SCREEN = screen  # Место экрана которое будет обрабатываться
        self.CHEST = chest  # Место где находится сундук
        self.COLOR_FOR_FIND = np.array(color)  # цвет который будет искаться на месте обработки
        self.MOUSE_CONTROLLER = MController()

    def bot_execute(self):
        counter = 0
        im = sc.grab(bbox=self.SCREEN)
        array = np.array(im)
        for i in range(array.shape[0]):
            for j in range(array.shape[1]):
                # если искомый пиксель есть в обрабатываемой области экрана, увеличиваем счетчик
                if np.array_equal(array[i][j], self.COLOR_FOR_FIND):
                    counter += 1
        # если в обрабатываемой области достаточно искомых пикселей, перемещаем курсор в нужное места экрана
        # и производим клин
        if counter > 1000:
            mouse_position = self.MOUSE_CONTROLLER.position
            self.MOUSE_CONTROLLER.position = self.CHEST
            self.MOUSE_CONTROLLER.click(MButton.left, 1)
            time.sleep(0.1)
            self.MOUSE_CONTROLLER.position = mouse_position

    def debug(self):
        """
        Метод вызываемый для отладки.

        Производит отображения области экрана которая будет обрабатываться, место куда будет установлен курсор
        и количество пикселей того или иного цвета.
        """
        time.sleep(1)
        im = sc.grab(bbox=self.SCREEN)
        im.show()

        array = np.array(im)
        unique = dict()
        for i in range(array.shape[0]):
            for j in range(array.shape[1]):
                key = f"{array[i][j][0]},{array[i][j][1]},{array[i][j][2]}"
                if unique.get(key, None):
                    unique[key] += 1
                else:
                    unique[key] = 1

        sorted_unique = {k: v for k, v in sorted(unique.items(), key=lambda item: item[1])}
        print(sorted_unique)

        position = self.MOUSE_CONTROLLER.position
        self.MOUSE_CONTROLLER.position = self.CHEST
        time.sleep(5)
        self.MOUSE_CONTROLLER.position = position
