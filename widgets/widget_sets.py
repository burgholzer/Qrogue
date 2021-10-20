from abc import abstractmethod, ABC

import py_cui
from py_cui.widget_set import WidgetSet

from game.actors.enemy import Enemy
from game.actors.player import Player as PlayerActor
from game.actors.player import DummyPlayer
from game.actors.riddle import Riddle
from game.actors.target import Target
from game.map.map import Map
from game.map.navigation import Direction
from game.map.tiles import Player as PlayerTile
from game.map.tutorial import Tutorial
from util.config import MapConfig
from util.my_random import RandomManager
from widgets.color_rules import ColorRules
from widgets.my_popups import Popup, CommonPopups
from widgets.my_widgets import SelectionWidget, StateVectorWidget, CircuitWidget, MapWidget, SimpleWidget, HudWidget


class MyWidgetSet(WidgetSet, ABC):
    """
    Class that handles different sets of widgets so we can easily switch between different screens.
    """
    def __init__(self, num_rows, num_cols, logger):
        super().__init__(num_rows, num_cols, logger)
        self.init_widgets()

    def render(self) -> None:
        for widget in self.get_widget_list():
            widget.render()

    @abstractmethod
    def init_widgets(self) -> None:
        pass

    @abstractmethod
    def get_widget_list(self) -> "list of Widgets":
        pass

    @abstractmethod
    def get_main_widget(self) -> py_cui.widgets.Widget:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass


_ascii_art = """
 Qrogue
"""
class MenuWidgetSet(MyWidgetSet):
    __NUM_OF_ROWS = 8
    __NUM_OF_COLS = 9
    __MAP_WIDTH = 50
    __MAP_HEIGHT = 14

    def __init__(self, logger, start_gameplay_callback: "void(Map, tiles.Player)",
                 start_fight_callback: "void(Player, Enemy, Direction)", open_riddle_callback: "void(Player, Riddle)",
                 visit_shop_callback: "void(Player, list of ShopItems)"):
        super().__init__(self.__NUM_OF_ROWS, self.__NUM_OF_COLS, logger)
        self.__start_gameplay_callback = start_gameplay_callback

        self.__seed = 7
        self.__start_fight_callback = start_fight_callback
        self.__open_riddle_callback = open_riddle_callback
        self.__visit_shop_callback = visit_shop_callback

    def init_widgets(self) -> None:
        title = self.add_block_label("Qrogue", 0, 0, row_span=6, column_span=self.__NUM_OF_COLS, center=True)
        self.__title = SimpleWidget(title)
        self.__title.set_data(_ascii_art)

        selection = self.add_block_label("", 6, 0, row_span=2, column_span=self.__NUM_OF_COLS, center=True)
        self.__selection = SelectionWidget(selection, 4)
        self.__selection.set_data(data=(
            ["PLAY", "TUTORIAL", "OPTIONS", "EXIT"],
            [self.__play, self.__tutorial, self.__options, self.__exit]
        ))

    def get_widget_list(self) -> "list of Widgets":
        return [
            self.__title,
            self.__selection
        ]

    def get_main_widget(self) -> py_cui.widgets.Widget:
        return self.__selection.widget

    def reset(self) -> None:
        self.__selection.render_reset()

    @property
    def selection(self) -> SelectionWidget:
        return self.__selection

    def __play(self) -> None:
        player = DummyPlayer()   # todo use real player
        seed = MapConfig.tutorial_seed() # todo and real seed
        map = Map(seed, self.__MAP_WIDTH, self.__MAP_HEIGHT, player, self.__start_fight_callback,
                  self.__open_riddle_callback, self.__visit_shop_callback)
        self.__start_gameplay_callback(map)

    def __tutorial(self) -> None:
        map = Map(MapConfig.tutorial_seed(), self.__MAP_WIDTH, self.__MAP_HEIGHT, DummyPlayer(), self.__start_fight_callback,
                  self.__open_riddle_callback, self.__visit_shop_callback)
        self.__start_gameplay_callback(map)
        Popup.message("Welcome to Qrogue! (scroll with arrow keys)", Tutorial.WelcomeMessage)

    def __options(self) -> None:
        print("todo")

    def __exit(self) -> None:
        #GameHandler.instance().stop()
        exit()


class ExploreWidgetSet(MyWidgetSet):
    __NUM_OF_ROWS = 8
    __NUM_OF_COLS = 9

    def __init__(self, logger):
        super().__init__(self.__NUM_OF_ROWS, self.__NUM_OF_COLS, logger)
        hud = self.add_block_label('HUD', 0, 0, row_span=1, column_span=self.__NUM_OF_COLS, center=False)
        hud.toggle_border()
        self.__hud = HudWidget(hud)

    def init_widgets(self) -> None:
        map_widget = self.add_block_label('MAP', 1, 0, row_span=self.__NUM_OF_ROWS-1, column_span=self.__NUM_OF_COLS, center=True)
        self.__map_widget = MapWidget(map_widget)

        ColorRules.apply_map_rules(self.__map_widget)
    
    def get_main_widget(self) -> py_cui.widgets.Widget:
        return self.__map_widget.widget

    def set_data(self, map: Map, player_tile: PlayerTile) -> None:
        self.__hud.set_data(player_tile.player)
        self.__map_widget.set_data(map)

    def get_widget_list(self) -> "list of Widgets":
        return [
            self.__hud,
            self.__map_widget
        ]

    def reset(self) -> None:
        self.__map_widget.widget.set_title("")

    def move_up(self) -> None:
        if self.__map_widget.move(Direction.Up):
            self.render()

    def move_right(self) -> None:
        if self.__map_widget.move(Direction.Right):
            self.render()

    def move_down(self) -> None:
        if self.__map_widget.move(Direction.Down):
            self.render()

    def move_left(self) -> None:
        if self.__map_widget.move(Direction.Left):
            self.render()


class ReachTargetWidgetSet(MyWidgetSet, ABC):
    __NUM_OF_ROWS = 9
    __NUM_OF_COLS = 9
    __CHOICE_COLUMNS = 2
    __DETAILS_COLUMNS = 2

    def __init__(self, logger, continue_exploration_callback: "()", choices: "list of str"):
        if len(choices) != 4:
            raise RuntimeError("Created a ReachTargetWidgetSet with more or less than 4 choices!")
        self.__choice_strings = choices
        super().__init__(self.__NUM_OF_ROWS, self.__NUM_OF_COLS, logger)
        self._continue_exploration_callback = continue_exploration_callback
        self._player = None
        self._target = None

    def init_widgets(self) -> None:
        hud = self.add_block_label('HUD', 0, 0, row_span=1, column_span=self.__NUM_OF_COLS, center=True)
        hud.toggle_border()
        self.__hud = HudWidget(hud)

        stv_row = 1
        stv = self.add_block_label('Player StV', stv_row, 0, row_span=4, column_span=3, center=True)
        self.__stv_player = StateVectorWidget(stv, "Current State")
        stv = self.add_block_label('Diff StV', stv_row, 3, row_span=3, column_span=3, center=True)
        self.__stv_diff = StateVectorWidget(stv, "Difference")
        stv = self.add_block_label('Target StV', stv_row, 6, row_span=3, column_span=3, center=True)
        self.__stv_target = StateVectorWidget(stv, "Target State")

        circuit = self.add_block_label('Circuit', 5, 0, row_span=2, column_span=self.__NUM_OF_COLS, center=True)
        self.__circuit = CircuitWidget(circuit)

        choices = self.add_block_label('Choices', 7, 0, row_span=2, column_span=3, center=True)
        choices.toggle_border()
        self._choices = SelectionWidget(choices, columns=self.__CHOICE_COLUMNS)
        self._choices.set_data(data=(
            self.__choice_strings,
            [self.__choices_adapt, self.__choices_commit, self.__choices_items, self._choices_flee]
        ))

        details = self.add_block_label('Details', 7, 3, row_span=2, column_span=6, center=True)
        details.toggle_border()
        self._details = SelectionWidget(details, columns=self.__DETAILS_COLUMNS)

        ColorRules.apply_stv_rules(self.__stv_player)
        ColorRules.apply_stv_rules(self.__stv_diff, diff_rules=True)
        ColorRules.apply_stv_rules(self.__stv_target)
        ColorRules.apply_circuit_rules(self.__circuit)
        ColorRules.apply_selection_rules(self._choices)
        ColorRules.apply_selection_rules(self._details)

    def get_main_widget(self) -> py_cui.widgets.Widget:
        return self._choices.widget

    def set_data(self, player: PlayerActor, target: Target) -> None:
        self._player = player
        self._target = target

        self.__hud.set_data(player)
        self.__circuit.set_data(player)

        p_stv = player.state_vector
        t_stv = target.statevector
        self.__stv_player.set_data(p_stv)
        self.__stv_diff.set_data(p_stv.get_diff(t_stv))
        self.__stv_target.set_data(t_stv)

    def get_widget_list(self) -> "list of Widgets":
        return [
            self.__hud,
            self.__stv_player,
            self.__stv_diff,
            self.__stv_target,
            self.__circuit,
            self._choices,
            self._details
        ]

    def reset(self) -> None:
        self.choices.render_reset()
        self.details.render_reset()

    @property
    def choices(self) -> SelectionWidget:
        return self._choices

    @property
    def details(self) -> SelectionWidget:
        return self._details

    def __choices_adapt(self) -> bool:
        self._details.set_data(data=(
            [str(instruction) for instruction in self._player.backpack] + ["-Back-"],
            [self.__choose_instruction]
        ))
        return True

    def __choose_instruction(self, index: int):
        if 0 <= index < self._player.backpack.size:
            self.__cur_instruction = self._player.get_instruction(index)
            if self.__cur_instruction is not None:
                self.__cur_instruction.reset_qubits()
                if self.__cur_instruction.is_used():
                    self._player.remove_instruction(index)
                    self.details.update_text(str(self._player.backpack.get(index)), index)
                else:
                    if self._player.is_space_left():
                        self.details.set_data(data=(
                            [self.__cur_instruction.preview_str(i) for i in range(self._player.num_of_qubits)],
                            [self.__choose_qubit]
                        ))
                    else:
                        CommonPopups.NoCircuitSpace.show()
                self.render()
            else:
                from util.logger import Logger
                Logger.instance().error("Error! The selected instruction/index is out of range!")
            return False
        else:
            return True

    def __choose_qubit(self, index: int = 0):
        selection = list(range(self._player.num_of_qubits))
        for q in self.__cur_instruction.qargs_iter():
            selection.remove(q)
        if self.__cur_instruction.use_qubit(selection[index]):
            selection.pop(index)
            self.details.set_data(data=(
                [self.__cur_instruction.preview_str(i) for i in selection],
                [self.__choose_qubit]
            ))
        else:
            self._player.use_instruction(self.__cur_instruction)
            self._details.set_data(data=(
                [str(instruction) for instruction in self._player.backpack] + ["-Back-"],
                [self.__choose_instruction]
            ))
        self.render()
        return False

    def __choices_commit(self) -> bool:
        if self._target is None:
            from util.logger import Logger
            Logger.instance().error("Error! Target is not set!")
            return False

        result = self._player.update_statevector()
        self.__stv_player.set_data(result)
        self.__stv_diff.set_data(result.get_diff(self._target.statevector))
        self.render()

        if self._target.is_reached(result):
            reward = self._target.get_reward()
            self._player.give_collectible(reward)
            self._details.set_data(data=(
                [f"Congratulations! Get reward: {reward}"],
                [self._continue_exploration_callback]
            ))
            return True
        else:
            return self._on_commit_fail()

    def __choices_items(self) -> bool:
        self._details.set_data(data=(
            ["You currently don't have any Items you could use!"],
            [self._empty_callback]
        ))
        return True

    @abstractmethod
    def _on_commit_fail(self) -> bool:
        pass

    @abstractmethod
    def _choices_flee(self) -> bool:
        pass

    def _empty_callback(self) -> None:
        pass


class FightWidgetSet(ReachTargetWidgetSet):
    def __init__(self, logger, continue_exploration_callback: "()", game_over_callback: "()"):
        super(FightWidgetSet, self).__init__(logger, continue_exploration_callback,
                                             ["Adapt", "Commit", "Items", "Flee"])
        self.__random = RandomManager.create_new()
        self.__game_over_callback = game_over_callback

    def set_data(self, player: PlayerActor, target: Enemy):
        super(FightWidgetSet, self).set_data(player, target)
        self.__flee_chance = target.flee_chance

    def _on_commit_fail(self) -> bool:
        diff = self._target.statevector.get_diff(self._player.state_vector)
        damage_taken = self._player.damage(diff=diff)
        if damage_taken < 0:
            self._details.set_data(data=(
                [f"Oh no, you took {damage_taken} damage and died!"],
                [self.__game_over_callback]
            ))
        else:
            self._details.set_data(data=(
                [f"Wrong, you took {damage_taken} damage. Remaining HP = {self._player.cur_hp}"],
                [self._empty_callback]
            ))
        return True

    def _choices_flee(self) -> bool:
        if self.__random.get() < self.__flee_chance:
            self._details.set_data(data=(
                ["You successfully fled!"],
                [self._continue_exploration_callback]
            ))
        else:
            self._player.damage(amount=1)
            if self._player.cur_hp > 0:
                self._details.set_data(data=(
                    ["Failed to flee. You lost 1 HP."],
                    [self._empty_callback]
                ))
            else:
                self._details.set_data(data=(
                    ["Failed to flee. You have no more HP left and die."],
                    [self.__game_over_callback]
                ))
        return True


class ShopWidgetSet(MyWidgetSet):
    __NUM_OF_ROWS = 9
    __NUM_OF_COLS = 9

    def __init__(self, logger, continue_exploration_callback: "()"):
        super().__init__(self.__NUM_OF_ROWS, self.__NUM_OF_COLS, logger)
        self.__continue_exploration = continue_exploration_callback
        self.__player = None
        self.__items = None

    def init_widgets(self) -> None:
        hud = self.add_block_label("HUD", 0, 0, row_span=1, column_span=self.__NUM_OF_COLS)
        self.__hud = HudWidget(hud)

        inv_width = 4
        inventory = self.add_block_label("Inventory", 1, 0, row_span=7, column_span=inv_width)
        self.__inventory = SelectionWidget(inventory)

        details = self.add_block_label("Details", 1, inv_width, row_span=4, column_span=self.__NUM_OF_COLS - inv_width)
        self.__details = SimpleWidget(details)
        buy = self.add_block_label("Buy", 4, inv_width, row_span=1, column_span=self.__NUM_OF_COLS - inv_width)
        self.__buy = SelectionWidget(buy)

    @property
    def inventory(self) -> SelectionWidget:
        return self.__inventory

    @property
    def buy(self) -> SelectionWidget:
        return self.__buy

    def get_widget_list(self) -> "list of Widgets":
        return [
            self.__hud,
            self.__inventory,
            self.__details,
            self.__buy,
        ]

    def get_main_widget(self) -> py_cui.widgets.Widget:
        return self.__inventory.widget

    def reset(self) -> None:
        self.__inventory.render_reset()

    def set_data(self, player: PlayerActor, items: "list of ShopItems") -> None:
        self.__player = player
        self.__hud.set_data(player)
        self.__update_inventory(items)

    def __update_inventory(self, items):
        self.__items = items
        self.__inventory.set_data(data=(
            [str(si) for si in items] + ["-Leave-"],
            [self.__select_item]
        ))

    def __select_item(self, index: int = 0) -> bool:
        if index >= len(self.__items):
            self.__continue_exploration()
            return False

        shop_item = self.__items[index]
        self.__cur_item = shop_item
        self.__details.set_data(shop_item.collectible)
        self.__buy.set_data(data=(
            ["Buy!", "No thanks"],
            [self.__buy_item, self.__back_to_inventory]
        ))
        return True

    def __buy_item(self) -> bool:
        if self.__player.backpack.use_coins(self.__cur_item.price):
            self.__player.give_collectible(self.__cur_item.collectible)
            self.__hud.render()
            self.__items.remove(self.__cur_item)
            self.__update_inventory(self.__items)
            return True
        else:
            return False

    def __back_to_inventory(self) -> bool:
        self.__cur_item = None
        return True


class RiddleWidgetSet(ReachTargetWidgetSet):
    __NUM_OF_ROWS = 9
    __NUM_OF_COLS = 9

    def __init__(self, logger, continue_exploration_callback: "()"):
        super().__init__(logger, continue_exploration_callback, ["Adapt", "Commit", "Items", "Give up"])

    def set_data(self, player: PlayerActor, target: Riddle) -> None:
        super(RiddleWidgetSet, self).set_data(player, target)
        self._target.is_reached(player.state_vector)

    def _on_commit_fail(self) -> bool:
        if self._target.attempts <= 0:
            self._details.set_data(data=(
                [f"You couldn't solve the riddle within the given attempts. It vanishes together with its reward."],
                [self._continue_exploration_callback]
            ))
        else:
            self._details.set_data(data=(
                [f"Wrong! Remaining attempts: {self._target.attempts}"],
                [self._empty_callback]
            ))
        return True

    def _choices_flee(self) -> bool:
        if self._target.attempts > 0:
            self._details.set_data(data=(
                [f"Abort - you can still try again later", "Continue"],
                [self._continue_exploration_callback, self._empty_callback]
            ))
        else:
            self._details.set_data(data=(
                ["Abort - but you don't have any attempts left to try again later!", "Continue"],
                [self._continue_exploration_callback, self._empty_callback]
            ))
        return True
