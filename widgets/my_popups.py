from enum import Enum

import py_cui
import py_cui.ui
from py_cui import ColorRule

from util.config import PopupConfig, ColorConfig
from util.logger import Logger


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
    def __get_color_rules():
        text = ColorConfig.TEXT_HIGHLIGHT
        return [
            ColorRule(f"{text}.*?{text}", 0, 0, "contains", "regex", [0, 1],
                      False, Logger.instance())
        ]

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

    def __init__(self, root, title, text, color, renderer, logger, controls):
        super().__init__(root, title, text, color, renderer, logger)
        self.__controls = controls
        self._top_view = 0
        self.__lines = MultilinePopup.__split_text(text, self._width - 6)

    @property
    def textbox_height(self) -> int:
        return self._height - self._pady - 2    # subtract both title and end line

    def up(self):
        if len(self.__lines) > self.textbox_height and self._top_view > 0:
            self._top_view -= 1

    def down(self):
        # since _top_view can never be negative we don't need to check if we have lines that don't fit on the popup
        if self._top_view < len(self.__lines) - self.textbox_height:
            self._top_view += 1

    def _handle_key_press(self, key_pressed):
        """Overrides base class handle_key_press function
        """
        if key_pressed in self.__controls.popup_close:
            self._root.close_popup()
        elif key_pressed == self.__controls.popup_scroll_up:
            self.up()
        elif key_pressed == self.__controls.popup_scroll_down:
            self.down()

    def _draw(self):
        """Overrides base class draw function
        """

        self._renderer.set_color_mode(self._color)
        self._renderer.draw_border(self)
        self._renderer.set_color_rules(self.__get_color_rules())
        counter = self._pady + 1
        for i in range(self._top_view, len(self.__lines)):
            if counter > self.textbox_height:
                break
            self._renderer.draw_text(self, self.__lines[i], self._start_y + counter, selected=True)
            counter += 1
            i += 1
        self._renderer.unset_color_mode(self._color)
        self._renderer.reset_cursor(self)


class CommonPopups(Enum):
    LockedDoor = ("Door is locked!", "Come back with a Key to open the Door.")
    EntangledDoor = ("Door is entangled!", "The Door entangled with this one was opened. Therefore you can no longer "
                                           "pass this Door.")
    TutorialBlocked = ("Halt!", "You should not go there yet! Finish the current step of the Tutorial first.")
    NotEnoughMoney = ("$$$", "You cannot afford that right now. Come back when you have enough money.")
    NoCircuitSpace = ("Nope", "Your Circuit has no more space left. Remove a Gate to place another one.")

    def __init__(self, title: str, text: str, color: int = PopupConfig.default_color()):
        self.__title = title
        self.__text = text
        self.__color = color

    def show(self):
        Popup.message(self.__title, self.__text, self.__color)
