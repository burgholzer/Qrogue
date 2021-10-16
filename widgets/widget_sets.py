from abc import abstractmethod, ABC

import py_cui
from py_cui.widget_set import WidgetSet

from game.actors.enemy import Enemy
from game.actors.player import Player as PlayerActor
from game.actors.player import DummyPlayer
from game.callbacks import SimpleCallback
from game.map import tiles
from game.map.map import Map
from game.map.navigation import Direction
from game.map.tiles import Player as PlayerTile
from util.config import MapConfig
from widgets.color_rules import ColorRules
from widgets.my_popups import Popup
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
                 start_fight_callback: "void(Player, Enemy, Direction)",
                 visit_shop_callback: "void(Player, list of ShopItems)",
                 show_popup_callback: "void(str, str, int)"):
        super().__init__(self.__NUM_OF_ROWS, self.__NUM_OF_COLS, logger)
        self.__start_gameplay_callback = start_gameplay_callback
        self.__show_popup_callback = show_popup_callback

        self.__seed = 7
        self.__start_fight_callback = start_fight_callback
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
        player_tile = tiles.Player(DummyPlayer())   # todo use real player
        seed = MapConfig.tutorial_seed() # todo and real seed
        map = Map(seed, self.__MAP_WIDTH, self.__MAP_HEIGHT, player_tile,
                  self.__start_fight_callback, self.__visit_shop_callback, self.__show_popup_callback)
        self.__start_gameplay_callback(map)

    def __tutorial(self) -> None:
        player_tile = tiles.Player(DummyPlayer())
        map = Map(MapConfig.tutorial_seed(), self.__MAP_WIDTH, self.__MAP_HEIGHT, player_tile,
                  self.__start_fight_callback, self.__visit_shop_callback, self.__show_popup_callback)
        self.__start_gameplay_callback(map)
        msg =   "Try to move around with the arrow keys and go to the door (|) on the right! " \
                "The fields with a \".\" will give you the next hints. " \
                "Now press ENTER, ESC or SPACE to close this dialog."
        Popup("Welcome to Qrogue!", msg)

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


class FightWidgetSet(MyWidgetSet):
    __NUM_OF_ROWS = 9
    __NUM_OF_COLS = 9

    def __init__(self, logger, end_of_fight_callback: SimpleCallback, end_of_gameplay_callback: SimpleCallback):
        super().__init__(self.__NUM_OF_ROWS, self.__NUM_OF_COLS, logger)
        self.__player = None
        self.__enemy = None
        self.__end_of_fight_callback = end_of_fight_callback
        self.__end_of_gameplay_callback = end_of_gameplay_callback

    def init_widgets(self) -> None:
        hud = self.add_block_label('HUD', 0, 0, row_span=1, column_span=self.__NUM_OF_COLS, center=True)
        hud.toggle_border()
        self.__hud = HudWidget(hud)

        stv_row = 1
        stv = self.add_block_label('Player StV', stv_row, 0, row_span=4, column_span=3, center=True)
        self.__stv_player = StateVectorWidget(stv, "Current State")
        stv = self.add_block_label('Diff StV', stv_row, 3, row_span=3, column_span=3, center=True)
        self.__stv_diff = StateVectorWidget(stv, "Difference")
        stv = self.add_block_label('Enemy StV', stv_row, 6, row_span=3, column_span=3, center=True)
        self.__stv_enemy = StateVectorWidget(stv, "Target State")

        circuit = self.add_block_label('Circuit', 5, 0, row_span=2, column_span=self.__NUM_OF_COLS, center=True)
        circuit.toggle_border()
        self.__circuit = CircuitWidget(circuit)

        choices = self.add_block_label('Choices', 7, 0, row_span=2, column_span=3, center=True)
        choices.toggle_border()
        self.__choices = SelectionWidget(choices, columns=SelectionWidget.FIGHT_CHOICE_COLUMNS)
        self.__choices.set_data(data=(
            ["Adapt", "Commit", "Items", "Flee"],
            [self.__choices_adapt, self.__choices_commit, self.__choices_items, self.__choices_flee]
        ))

        details = self.add_block_label('Details', 7, 3, row_span=2, column_span=6, center=True)
        details.toggle_border()
        self.__details = SelectionWidget(details, columns=SelectionWidget.FIGHT_DETAILS_COLUMNS)

        ColorRules.apply_stv_rules(self.__stv_player)
        ColorRules.apply_stv_rules(self.__stv_diff, diff_rules=True)
        ColorRules.apply_stv_rules(self.__stv_enemy)
        ColorRules.apply_circuit_rules(self.__circuit)
        ColorRules.apply_selection_rules(self.__choices)
        ColorRules.apply_selection_rules(self.__details)

    def get_main_widget(self) -> py_cui.widgets.Widget:
        return self.__choices.widget

    def set_data(self, player: PlayerActor, enemy: Enemy) -> None:
        self.__player = player
        self.__enemy = enemy

        self.__hud.set_data(player)
        self.__circuit.set_data(player)

        p_stv = player.state_vector
        e_stv = enemy.get_statevector()
        self.__stv_player.set_data(p_stv)
        self.__stv_diff.set_data(p_stv.get_diff(e_stv))
        self.__stv_enemy.set_data(e_stv)

    def get_widget_list(self) -> "list of Widgets":
        return [
            self.__hud,
            self.__stv_player,
            self.__stv_diff,
            self.__stv_enemy,
            self.__circuit,
            self.__choices,
            self.__details
        ]

    def reset(self) -> None:
        self.choices.render_reset()
        self.details.render_reset()

    @property
    def choices(self) -> SelectionWidget:
        return self.__choices

    @property
    def details(self) -> SelectionWidget:
        return self.__details

    def __choices_adapt(self) -> bool:
        self.__details.set_data(data=(
            [str(instruction) for instruction in self.__player.backpack],
            [self.__player.use_instruction]
        ))
        return True

    def __choices_commit(self) -> bool:
        fight_end, msg = self.__attack()
        if fight_end:
            self.__details.set_data(data=(
                [f"Get reward: {msg}"],
                [self.__end_of_fight_callback]
            ))
        else:
            if msg.startswith("-"):
                self.__details.set_data(data=(
                    [f"Oh no, you took {msg[1:]} damage and died!"],
                    [self.__game_over]
                ))
            else:
                self.__details.set_data(data=(
                    [f"Wrong, you took {msg} damage. Remaining HP = {self.__player.cur_hp}"],
                    [self.__damage_taken]
                ))
        return True

    def __choices_items(self) -> bool:
        print("items")
        return False

    def __choices_flee(self) -> bool:
        # todo check chances of fleeing
        self.__end_of_fight_callback()
        return False

    def __attack(self) -> (bool, str):
        """

        :return: True if fight is over (attack was successful -> enemy is dead), False otherwise
        """
        if self.__enemy is None:
            from util.logger import Logger
            Logger.instance().error("Error! Enemy is not set!")
            return False

        result = self.__player.update_statevector()
        self.__stv_player.set_data(result)
        self.__stv_diff.set_data(result.get_diff(self.__enemy.get_statevector()))
        self.render()

        success = self.__enemy.damage(result)
        if success:
            reward = self.__enemy.get_reward()
            self.__player.give_collectible(reward)
            return True, str(reward)
        else:
            diff = self.__enemy.get_statevector().get_diff(self.__player.state_vector)
            damage_taken = self.__player.damage(diff)
            return False, str(damage_taken)

    def __game_over(self):
        self.__end_of_gameplay_callback()

    def __damage_taken(self) -> None:
        pass


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
