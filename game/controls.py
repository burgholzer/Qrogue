
from py_cui.keys import *

from game.actors.player import Player


class Controls:
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

        self.__render = KEY_R_LOWER
        self.__print_screen = KEY_CTRL_P
        self.__cheat = KEY_CTRL_Q

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
    def render(self) -> int:
        return self.__render

    @property
    def print_screen(self) -> int:
        return self.__print_screen

    @property
    def cheat(self) -> int:
        return self.__cheat


class Pausing:
    __instance = None

    @staticmethod
    def instance() -> "Pausing":
        if Pausing.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return Pausing.__instance

    @staticmethod
    def pause():
        if Pausing.__instance is not None:
            self = Pausing.__instance
            self.__callback(self.__player)

    def __init__(self, player: Player, callback: "()"):
        self.__player = player
        self.__callback = callback
        Pausing.__instance = self

    @staticmethod
    def key() -> int:
        return KEY_P_LOWER
