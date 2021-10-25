import py_cui.colors

from game.map.tiles import TileCode
from util.config import PathConfig, ColorConfig
from widgets.my_widgets import MapWidget, StateVectorWidget, SelectionWidget, CircuitWidget


__color_manager = {
    TileCode.Invalid: py_cui.RED_ON_BLUE,
    TileCode.Void: py_cui.CYAN_ON_BLACK,
    TileCode.Floor: py_cui.CYAN_ON_BLACK,
    TileCode.Wall: py_cui.BLACK_ON_WHITE,
    TileCode.Obstacle: py_cui.CYAN_ON_BLACK,
    TileCode.FogOfWar: py_cui.CYAN_ON_BLACK,
    TileCode.Door: py_cui.CYAN_ON_BLACK,
    TileCode.Collectible: py_cui.CYAN_ON_BLACK,
    TileCode.Player: py_cui.GREEN_ON_BLACK,
    TileCode.Enemy: py_cui.RED_ON_BLACK,
    TileCode.Boss: py_cui.BLACK_ON_RED,
}
def get_color(tile: TileCode) -> int:
    return __color_manager[tile]


class Fragment:
    def __init__(self, start: int, text: str, color: int):
        self.__start = start
        self.__text = text
        self.__color = color

    @property
    def start(self) -> int:
        return self.__start

    @property
    def length(self) -> int:
        return len(self.text)

    @property
    def end(self) -> int:
        return self.start + len(self.text)

    @property
    def text(self) -> str:
        return self.__text

    @property
    def color(self) -> int:
        return self.__color

    def format(self) -> "[str, int]":
        if self.text.startswith(ColorConfig.TEXT_HIGHLIGHT) and self.text.endswith(ColorConfig.TEXT_HIGHLIGHT):
            color = ColorConfig.get(self.text[1:3])
            text = self.text[3:-1]
            return [text, color]
        return [self.text, self.color]

    def __len__(self):
        return self.length

    def __lt__(self, other) -> bool:
        if self.start == other.start:
            return self.end < other.end
        return self.start < other.start

    def __str__(self) -> str:
        return f"({self.start}-{self.end}) {self.text} ({self.color})"


class FragmentStorage:
    def __init__(self, og_text: str, og_color: int):
        self.__og_text = og_text
        self.__og_color = og_color
        self.__fragments = []

    def append(self, fragment: Fragment):
        if fragment.color != self.__og_color:
            self.__fragments.append(fragment)

    def sort(self):
        self.__fragments.sort()

    def fill_blanks(self) -> "list of [int, str]":
        if len(self.__fragments) <= 0:
            return [[self.__og_text, self.__og_color]]
        formatted_frags = []
        prev = self.__fragments[0]

        # append the text before the first color
        if prev.start != 0:
            formatted_frags.append([self.__og_text[0:prev.start], self.__og_color])
        # appended the colored text with potentially the normal text in between
        for i in range(1, len(self.__fragments)):
            formatted_frags.append(prev.format())
            cur = self.__fragments[i]
            if prev.end != cur.start:
                formatted_frags.append([self.__og_text[prev.end:cur.start], self.__og_color])
            prev = cur
        formatted_frags.append(prev.format())   # append the last color
        # append the text after the last color
        if prev.end != len(self.__og_text):
            formatted_frags.append([self.__og_text[prev.end:], self.__og_color])

        return formatted_frags

    def __iter__(self):
        return iter(self.__fragments)


class MultiColorRenderer(py_cui.renderer.Renderer):
    __FILE_NAME = "multi_color_debug.txt"

    def __init__(self, root, stdscr, logger):
        super().__init__(root, stdscr, logger)
        PathConfig.delete(self.__FILE_NAME)

    def _generate_text_color_fragments(self, ui_element, line, render_text, selected):
        """Function that applies color rules to text, dividing them if match is found

        Parameters
        ----------
        ui_element : py_cui.ui.UIElement
            The ui_element being drawn
        line : str
            the line of text being drawn
        render_text : str
            The text shortened to fit within given space

        Returns
        -------
        fragments : list of [int, str]
            list of text - color code combinations to write
        """
        #start_time = time.time()
        if selected:
            meta_fragments = FragmentStorage(render_text, ui_element.get_selected_color())
        else:
            meta_fragments = FragmentStorage(render_text, ui_element.get_color())

        for color_rule in self._color_rules:
            fragments, match = color_rule.generate_fragments(ui_element, line, render_text, selected)
            if match:
                cur_pos = 0
                for frag in fragments:
                    start = cur_pos
                    text = frag[0]
                    color = frag[1]
                    cur_pos += len(text)
                    meta_fragments.append(Fragment(start, text, color))
        meta_fragments.sort()
        #print("Full:")
        #print(full)
        #print()
        #print("Frags:")
        full = meta_fragments.fill_blanks()
        text = ""
        for frag in full:
            text += str(frag)
        text += "\n"
        PathConfig.write(self.__FILE_NAME, text, append=True)
        #"""
        #duration = time.time() - start_time
        #print(duration)
        #print()
        return full


class ColorRules:
    @staticmethod
    def apply_map_rules(map_widget: MapWidget) -> None:
        w = map_widget.widget
        w.add_text_color_rule('P', get_color(TileCode.Player), 'contains', match_type='regex')
        w.add_text_color_rule('B', get_color(TileCode.Boss), 'contains', match_type='regex')
        w.add_text_color_rule('\d', get_color(TileCode.Enemy), 'contains', match_type='regex')
        w.add_text_color_rule('#', get_color(TileCode.Wall), 'contains', match_type='regex')

    @staticmethod
    def apply_stv_rules(stv_widget: StateVectorWidget, diff_rules: bool = False) -> None:
        stv_widget.widget.add_text_color_rule("~.*~", py_cui.colors.CYAN_ON_BLACK, 'contains', match_type='regex')

        if diff_rules:
            stv_widget.widget.add_text_color_rule("0j", py_cui.colors.BLACK_ON_GREEN, "startswith", match_type="regex")

    @staticmethod
    def apply_selection_rules(sel_widget: SelectionWidget) -> None:
        length = 0 #sel_widget.choice_length + 2 # +2 to include the leading and trailing whitespace
        sel_widget.widget.add_text_color_rule(f"->.{{{length}}}", py_cui.colors.BLACK_ON_WHITE,
                                              'contains', match_type='regex')

    @staticmethod
    def apply_circuit_rules(circuit_widget: CircuitWidget) -> None:
        regex = "(\{.*?\}|\|.*?\>|\<.*?\|)"
        circuit_widget.widget.add_text_color_rule(regex, py_cui.colors.BLACK_ON_WHITE, 'contains', match_type='regex')
        #circuit_widget.widget.add_text_color_rule("\|.*?\>", py_cui.colors.BLACK_ON_YELLOW,
        #                                      'contains', match_type='regex')
        #circuit_widget.widget.add_text_color_rule("\<.*?\|", py_cui.colors.BLACK_ON_YELLOW,
        #                                      'contains', match_type='regex')
