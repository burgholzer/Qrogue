from abc import ABC

import py_cui


class Popup(ABC):
    def __init__(self, show_popup: "void(str, str, int)", title: str, text: str, color: int = py_cui.WHITE_ON_CYAN, show: bool = True):
        self.__title = title
        self.__text = text
        self.__color = color
        self.__show_popup = show_popup
        self.__focused_widget = None
        if show:
            self.show()

    def show(self):
        self.__show_popup(self.__title, self.__text, self.__color)
