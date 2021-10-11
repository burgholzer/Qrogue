from abc import ABC

import py_cui
import py_cui.ui


class Popup(ABC):
    def __init__(self, show_popup: "void(str, str, int)", title: str, text: str,
                 color: int = py_cui.WHITE_ON_CYAN, show: bool = True):
        self.__title = title
        self.__text = text
        self.__color = color
        self.__show_popup = show_popup
        self.__focused_widget = None
        if show:
            self.show()

    def show(self):
        self.__show_popup(self.__title, self.__text, self.__color)


class MultilinePopup(py_cui.popups.Popup, py_cui.ui.MenuImplementation):

    @staticmethod
    def __split_text(text: str, width: int) -> "list of str":
        return [text[i:i + width] for i in range(0, len(text), width)]

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
