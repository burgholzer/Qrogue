from enum import Enum

import py_cui
import py_cui.ui
from util.config import PopupConfig


class Popup:
    __show_popup = None

    @staticmethod
    def update_popup_functions(show_popup_callback: "void(str, str, int)") -> None:
        Popup.__show_popup = show_popup_callback

    @staticmethod
    def show_popup() -> "void(str, str, int)":
        return Popup.__show_popup

    @staticmethod
    def message(title: str, text: str, color: int = PopupConfig.default_color()):
        Popup(title, text, color, show=True)

    def __init__(self, title: str, text: str, color: int = PopupConfig.default_color(), show: bool = True):
        self.__title = title
        self.__text = text
        self.__color = color
        if show:
            self.show()

    def show(self, show_popup_callback: "void(str, str, int)" = None) -> None:
        if show_popup_callback is None:
            Popup.__show_popup(self.__title, self.__text, self.__color)
        else:
            show_popup_callback(self.__title, self.__text, self.__color)


class MultilinePopup(py_cui.popups.Popup, py_cui.ui.MenuImplementation):
    @staticmethod
    def __split_text(text: str, width: int) -> "list of str":
        split_text = []
        for paragraph in text.splitlines():
            index = 0
            while index + width < len(paragraph):
                last_whitespace = paragraph.rfind(" ", index + 1, index + width)
                if last_whitespace == -1:
                    cur_width = width
                else:
                    cur_width = last_whitespace - index
                next_line = paragraph[index:index + cur_width].strip()
                if len(next_line) > 0:
                    split_text.append(next_line)
                index += cur_width
            # The last line is appended as it is
            split_text.append(paragraph[index:index + width].strip())
        return split_text

    def __init__(self, root, title, text, color, renderer, logger):
        super().__init__(root, title, text, color, renderer, logger)
        #self._top_view = 0
        self.__lines = MultilinePopup.__split_text(text, self._width - 6)

    def _draw(self):
        """Overrides base class draw function
        """

        self._renderer.set_color_mode(self._color)
        self._renderer.draw_border(self)
        self._renderer.set_color_rules([])
        counter = self._pady + 1
        #line_counter = 0
        i = 0
        while i < len(self.__lines):
            line = self.__lines[i]
            #if line_counter < self._top_view:
            #    line_counter = line_counter + 1
            #else:
            if counter >= self._height - self._pady - 1:
                break
            self._renderer.draw_text(self, line, self._start_y + counter, selected=True)
            counter += 1
            i += 1
            #line_counter += 1
        self._renderer.unset_color_mode(self._color)
        self._renderer.reset_cursor(self)


class CommonPopups(Enum):
    LockedDoor = ("Door is locked!", "Come back with a Key to open the Door.")
    TutorialBlocked = ("Halt!", "You should not go there yet! Finish the current step of the Tutorial first.")
    NotEnoughMoney = ("$$$", "You cannot afford that right now. Come back when you have enough money.")

    def __init__(self, title: str, text: str, color: int = PopupConfig.default_color()):
        self.__title = title
        self.__text = text
        self.__color = color

    def show(self):
        Popup.message(self.__title, self.__text, self.__color)
