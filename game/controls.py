
from py_cui.keys import *

from game.actors.player import Player


class Controls:
    INVALID_KEY = 127

    def __init__(self):
        self.__move_up = KEY_UP_ARROW
        self.__move_right = KEY_RIGHT_ARROW
        self.__move_down = KEY_DOWN_ARROW
        self.__move_left = KEY_LEFT_ARROW

        self.__selection_up = KEY_UP_ARROW
        self.__selection_right = KEY_RIGHT_ARROW
        self.__selection_down = KEY_DOWN_ARROW
        self.__selection_left = KEY_LEFT_ARROW

        self.__popup_close = [KEY_ESCAPE, KEY_SPACE, KEY_ENTER]
        self.__popup_scroll_up = KEY_UP_ARROW
        self.__popup_scroll_down = KEY_DOWN_ARROW

        self.__action = KEY_SPACE
        self.__pause = KEY_P_LOWER

        self.__render = KEY_R_LOWER
        self.__print_screen = KEY_CTRL_P

    def convert(self, key_pressed: int) -> int:
        """
        Converts a pressed key to a code representing the corresponding action
        :param key_pressed: the key that was pressed
        :return: a code corresponding to one of the possible actions
        """
        if key_pressed == self.move_up:
            return 1
        elif key_pressed == self.move_right:
            return 2
        elif key_pressed == self.move_down:
            return 3
        elif key_pressed == self.move_left:
            return 4
        elif key_pressed == self.selection_up:
            return 5
        elif key_pressed == self.selection_right:
            return 6
        elif key_pressed == self.selection_down:
            return 7
        elif key_pressed == self.selection_left:
            return 8
        elif key_pressed == self.popup_close:
            return 9
        elif key_pressed == self.popup_scroll_up:
            return 10
        elif key_pressed == self.popup_scroll_down:
            return 11
        elif key_pressed == self.action:
            return 12
        elif key_pressed == self.pause:
            return 13

        else:
            return Controls.INVALID_KEY

    @property
    def move_up(self) -> int:
        return self.__move_up

    @property
    def move_right(self) -> int:
        return self.__move_right

    @property
    def move_down(self) -> int:
        return self.__move_down

    @property
    def move_left(self) -> int:
        return self.__move_left

    @property
    def selection_up(self) -> int:
        return self.__selection_up

    @property
    def selection_right(self) -> int:
        return self.__selection_right

    @property
    def selection_down(self) -> int:
        return self.__selection_down

    @property
    def selection_left(self) -> int:
        return self.__selection_left

    @property
    def popup_close(self) -> "list of ints":
        return self.__popup_close

    @property
    def popup_scroll_up(self) -> int:
        return self.__popup_scroll_up

    @property
    def popup_scroll_down(self) -> int:
        return self.__popup_scroll_down

    @property
    def action(self) -> int:
        return self.__action

    @property
    def pause(self) -> int:
        return self.__pause

    @property
    def render(self) -> int:
        return self.__render

    @property
    def print_screen(self) -> int:
        return self.__print_screen


class Pausing:
    __instance = None

    @staticmethod
    def pause():
        if Pausing.__instance is not None:
            Pausing.__instance.__pause_now()

    def __init__(self, player: Player, callback: "()"):
        self.__player = player
        self.__callback = callback
        Pausing.__instance = self

    def __pause_now(self):
        self.__callback(self.__player)
