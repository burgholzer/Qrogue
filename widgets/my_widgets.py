from abc import ABC, abstractmethod

from py_cui.widgets import BlockLabel

from game.actors.player import Player as PlayerActor
from game.logic.instruction import HGate, Instruction
from game.logic.qubit import StateVector
from game.map.map import Map
from game.map.navigation import Direction
from widgets.renderer import TileRenderer


class Widget(ABC):
    def __init__(self, widget: BlockLabel):
        self.__widget = widget

    @property
    def widget(self) -> BlockLabel:
        return self.__widget

    @abstractmethod
    def set_data(self, data) -> None:
        pass

    @abstractmethod
    def render(self) -> None:
        pass

    @abstractmethod
    def render_reset(self) -> None:
        pass


class SimpleWidget(Widget):
    def __init__(self, widget: BlockLabel):
        super().__init__(widget)
        self.__text = ""

    def set_data(self, data) -> None:
        self.__text = str(data)

    def render(self) -> None:
        self.widget.set_title(self.__text)

    def render_reset(self) -> None:
        self.widget.set_title("")


class HudWidget(Widget):
    def __init__(self, widget: BlockLabel):
        super().__init__(widget)
        self.__player = None

    def set_data(self, player:PlayerActor) -> None:
        self.__player = player

    def render(self) -> None:
        if self.__player is not None:
            text = f"{self.__player.cur_hp} HP   \t" \
                   f"{self.__player.backpack.coin_count}$, {self.__player.backpack.key_count} keys"
            self.widget.set_title(text)

    def render_reset(self) -> None:
        self.widget.set_title("")


class CircuitWidget(Widget):
    def __init__(self, widget: BlockLabel):
        super().__init__(widget)
        self.__player = None

    def set_data(self, player: PlayerActor) -> None:
        self.__player = player

    def render(self) -> None:
        if self.__player is not None:
            entry = "-" * (3 + Instruction.MAX_ABBREVIATION_LEN + 3)
            row = [entry] * self.__player.space
            rows = []
            for i in range(self.__player.num_of_qubits):
                rows.append(row.copy())

            for i, inst in self.__player.circuit_enumerator():
                for q in inst.qargs_iter():
                    inst_str = inst.abbreviation(q)
                    diff_len = Instruction.MAX_ABBREVIATION_LEN - len(inst_str)
                    inst_str = f"--{{{inst_str}}}--"
                    if diff_len > 0:
                        half_diff = int(diff_len / 2)
                        inst_str = inst_str.ljust(len(inst_str) + half_diff, "-")
                        if diff_len % 2 == 0:
                            inst_str = inst_str.rjust(len(inst_str) + half_diff, "-")
                        else:
                            inst_str = inst_str.rjust(len(inst_str) + half_diff + 1, "-")
                    rows[q][i] = inst_str
            circ_str = ""
            q = 0
            for row in rows:
                circ_str += f"| q{q} >---" # add qubit
                q += 1
                for i in range(len(row)):
                    circ_str += row[i]
                    if i < len(row) - 1:
                         circ_str += "+"
                circ_str += "< M |\n"
            self.widget.set_title(circ_str)

    def render_reset(self) -> None:
        self.widget.set_title("")


class MapWidget(Widget):
    def __init__(self, widget: BlockLabel):
        super().__init__(widget)
        self.__map = None
        self.__backup = None

    def set_data(self, map: Map) -> None:
        self.__map = map

    def render(self) -> None:   # todo more efficient rendering!
        if self.__map is not None:
            str_rep = ""
            for y in range(self.__map.height):
                for x in range(self.__map.width):
                    tile = self.__map.at(x, y)
                    str_rep += TileRenderer.render(tile)
                str_rep += "\n"
            self.widget.set_title(str_rep)

    def render_reset(self) -> None:
        self.__backup = self.widget.get_title().title()
        self.widget.set_title("")

    def move(self, direction: Direction) -> bool:
        return self.__map.move(direction)


class StateVectorWidget(Widget):
    def __init__(self, widget: BlockLabel, headline: str):
        super().__init__(widget)
        self.__headline = headline
        self.__state_vector = None

    def set_data(self, state_vector: StateVector) -> None:
        self.__state_vector = state_vector

    def render(self) -> None:
        if self.__state_vector is not None:
            str_rep = f"~{self.__headline}~\n{self.__state_vector}"
            self.widget.set_title(str_rep)

    def render_reset(self) -> None:
        self.widget.set_title("")


class SelectionWidget(Widget):
    FIGHT_CHOICE_COLUMNS = 2
    FIGHT_DETAILS_COLUMNS = 3
    __COLUMN_SEPARATOR = "   "

    def __init__(self, widget: BlockLabel, columns: int = 1):
        super(SelectionWidget, self).__init__(widget)
        self.__columns = columns
        self.__index = 0
        self.__choice_length = 0
        self.__choices = []
        self.__callbacks = []

    @property
    def choice_length(self) -> int:
        return self.__choice_length

    def update_text(self, text: str, index: int):
        if 0 <= index < len(self.__choices):
            self.__choices[index] = text

    def set_data(self, data: "tuple of list of str and list of SelectionCallbacks") -> None:
        self.render_reset()
        self.__choices = data[0]
        self.__callbacks = data[1]
        self.__choice_length = 0
        for choice in self.__choices:
            if len(choice) > self.__choice_length:
                self.__choice_length = len(choice)
        for i in range(len(self.__choices)):
            self.__choices[i] = self.__choices[i].ljust(self.__choice_length)

    def render(self) -> None:
        str_rep = ""
        for i in range(len(self.__choices)):
            if i == self.__index and self.widget.is_selected():
                wrapper = "-> "
            else:
                wrapper = "   "
            str_rep += wrapper
            str_rep += self.__choices[i]
            str_rep += " "
            if i % self.__columns == self.__columns - 1:
                str_rep += "\n"
            else:
                str_rep += self.__COLUMN_SEPARATOR
        self.widget.set_title(str_rep)

    def render_reset(self) -> None:
        self.widget.set_title("")
        self.__index = 0

    def up(self) -> None:
        self.__index -= self.__columns
        if self.__index < 0:
            self.__index += len(self.__choices)
        self.render()

    def right(self) -> None:
        if self.__columns == 1:
            self.down()
        else:
            self.__index += 1
            if self.__index % self.__columns == 0:
                self.up()
            else:
                self.render()

    def down(self) -> None:
        self.__index += self.__columns
        if self.__index >= len(self.__choices):
            self.__index -= len(self.__choices)
        self.render()

    def left(self) -> None:
        if self.__columns == 1:
            self.up()
        else:
            self.__index -= 1
            if self.__index % self.__columns == self.__columns - 1:
                self.down()
            else:
                self.render()

    def use(self) -> bool:
        """
        :return: True if the focus should move, False if the focus should stay in this SelectionWidget
        """
        # if only one callback is given, it needs the index as parameter
        if len(self.__callbacks) == 1 and len(self.__choices) > 1:
            ret = self.__callbacks[0](self.__index)
        else:
            ret = self.__callbacks[self.__index]()
        if ret is None: # move focus if nothing is returned
            return True
        else:
            return ret
