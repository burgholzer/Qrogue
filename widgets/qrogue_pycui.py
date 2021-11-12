from enum import Enum

import py_cui

from game.actors.boss import Boss
from game.actors.enemy import Enemy
from game.actors.player import Player as PlayerActor
from game.actors.riddle import Riddle
from game.callbacks import CallbackPack
from game.controls import Controls, Pausing
from game.map.map import Map
from game.map.navigation import Direction
from util.config import PathConfig, ColorConfig, CheatConfig
from util.key_logger import KeyLogger
from util.logger import Logger
from widgets.color_rules import MultiColorRenderer
from widgets.my_popups import Popup, MultilinePopup
from widgets.widget_sets import ExploreWidgetSet, FightWidgetSet, MyWidgetSet, MenuWidgetSet, ShopWidgetSet, \
    RiddleWidgetSet, BossFightWidgetSet, PauseMenuWidgetSet


class QrogueCUI(py_cui.PyCUI):
    def __init__(self, seed: int, controls: Controls, width: int = 8, height: int = 9):
        super().__init__(width, height)
        Logger.instance().set_popup(self.show_message_popup, self.show_error_popup)
        Popup.update_popup_functions(self.__show_popup)
        CheatConfig.init(self.__show_popup, self.__show_cheat_popup)

        self.__state_machine = StateMachine(self)
        self.__seed = seed
        self.__controls = controls
        self.__focused_widget = None

        cbp = CallbackPack(self.__start_gameplay, self.__start_fight, self.__start_boss_fight, self.__open_riddle,
                           self.__visit_shop)
        self.__menu = MenuWidgetSet(Logger.instance(), cbp, self.stop)
        self.__pause = PauseMenuWidgetSet(Logger.instance(), self.__general_continue, self.switch_to_menu)
        self.__explore = ExploreWidgetSet(Logger.instance())
        self.__fight = FightWidgetSet(Logger.instance(), self.__continue_explore, self.__end_of_gameplay)
        self.__boss_fight = BossFightWidgetSet(Logger.instance(), self.__continue_explore, self.__end_of_gameplay,
                                               self.__won_tutorial)
        self.__riddle = RiddleWidgetSet(Logger.instance(), self.__continue_explore)
        self.__shop = ShopWidgetSet(Logger.instance(), self.__continue_explore)

        self.__cur_widget_set = None
        self.__init_keys()

        self.__state_machine.change_state(State.Menu, None)

    def start(self):
        self.render()
        super(QrogueCUI, self).start()

    def _handle_key_presses(self, key_pressed):
        KeyLogger.instance().log(self.__controls, key_pressed)
        super(QrogueCUI, self)._handle_key_presses(key_pressed)

    def _initialize_widget_renderer(self):
        """Function that creates the renderer object that will draw each widget
        """
        if self._renderer is None:
            self._renderer = MultiColorRenderer(self, self._stdscr, self._logger)
        super(QrogueCUI, self)._initialize_widget_renderer()

    def __init_keys(self) -> None:
        # debugging stuff
        self.add_key_command(self.__controls.print_screen, self.print_screen)
        self.__menu.get_main_widget().add_key_command(self.__controls.print_screen, self.print_screen)
        self.__explore.get_main_widget().add_key_command(self.__controls.print_screen, self.print_screen)
        self.__fight.get_main_widget().add_key_command(self.__controls.print_screen, self.print_screen)
        self.__boss_fight.get_main_widget().add_key_command(self.__controls.print_screen, self.print_screen)

        self.__pause.get_main_widget().add_key_command(CheatConfig.INPUT_CHEAT_KEY, CheatConfig.cheat_input)
        self.__pause.get_main_widget().add_key_command(CheatConfig.CHEAT_LIST_KEY, CheatConfig.cheat_list)
        # don't add the pause key to Menu and Pause itself!
        for widget_set in [self.__explore, self.__fight, self.__boss_fight, self.__shop, self.__riddle]:
            for widget in widget_set.get_widget_list():
                widget.widget.add_key_command(self.__controls.pause, Pausing.pause)


        # all selections
        selection_widgets = [
            self.__menu.selection,
            self.__fight.choices, self.__fight.details,
            self.__boss_fight.choices, self.__boss_fight.details,
            self.__shop.inventory, self.__shop.buy,
            self.__riddle.choices, self.__riddle.details,
            self.__pause.choices, self.__pause.details,
        ]
        for my_widget in selection_widgets:
            widget = my_widget.widget
            widget.add_key_command(self.__controls.selection_up, my_widget.up)
            widget.add_key_command(self.__controls.selection_right, my_widget.right)
            widget.add_key_command(self.__controls.selection_down, my_widget.down)
            widget.add_key_command(self.__controls.selection_left, my_widget.left)

        # menu
        self.__menu.selection.widget.add_key_command(self.__controls.action, self.__use_menu_selection)

        # pause
        self.__pause.choices.widget.add_key_command(self.__controls.action, self.__pause_choices)
        self.__pause.details.widget.add_key_command(self.__controls.action, self.__pause_details)

        # explore
        w = self.__explore.get_main_widget()
        w.add_key_command(self.__controls.move_up, self.__explore.move_up)
        w.add_key_command(self.__controls.move_right, self.__explore.move_right)
        w.add_key_command(self.__controls.move_down, self.__explore.move_down)
        w.add_key_command(self.__controls.move_left, self.__explore.move_left)

        # fight
        self.__fight.choices.widget.add_key_command(self.__controls.action, self.__fight_choices)
        self.__fight.details.widget.add_key_command(self.__controls.action, self.__fight_details)
        self.__boss_fight.choices.widget.add_key_command(self.__controls.action, self.__boss_fight_choices)
        self.__boss_fight.details.widget.add_key_command(self.__controls.action, self.__boss_fight_details)

        # shop
        self.__shop.inventory.widget.add_key_command(self.__controls.action, self.__shop_inventory)
        self.__shop.buy.widget.add_key_command(self.__controls.action, self.__shop_buy)

        # riddle
        self.__riddle.choices.widget.add_key_command(self.__controls.action, self.__riddle_choices)
        self.__riddle.details.widget.add_key_command(self.__controls.action, self.__riddle_details)

    def print_screen(self) -> None:
        text = ""
        for my_widget in self.__cur_widget_set.get_widget_list():
            text += str(my_widget) + "\n"
            text += my_widget.widget.get_title()
            text += "\n"
        PathConfig.new_screen_print(text)

    def apply_widget_set(self, new_widget_set: MyWidgetSet) -> None:
        new_widget_set.reset()
        super().apply_widget_set(new_widget_set)
        self.__cur_widget_set = new_widget_set
        self.move_focus(self.__cur_widget_set.get_main_widget(), auto_press_buttons=False)
        self.__cur_widget_set.render()

    def __show_popup(self, title: str, text: str, color: int) -> None:
        self.__focused_widget = self.get_selected_widget()
        self._popup = MultilinePopup(self, title, text, color, self._renderer, self._logger, self.__controls)

    def __show_cheat_popup(self, title: str, color: int) -> None:
        self.__focused_widget = self.get_selected_widget()
        self._popup = py_cui.popups.TextBoxPopup(self, title, color, self.__use_cheat, self._renderer, False,
                                                 self._logger)

    def __use_cheat(self, input: str):
        if CheatConfig.use_cheat(input):
            Popup.message("Cheats", f"Successfully used the Cheat \"{input}\"")
        else:
            Popup.message("Cheats", "This is not a valid Cheat!")

    def close_popup(self) -> None:
        super(QrogueCUI, self).close_popup()
        self.move_focus(self.__focused_widget)

    def __dummy(self) -> None:
        pass

    def __general_continue(self):
        self.__state_machine.change_state(self.__state_machine.prev_state, None)

    def switch_to_menu(self, data=None) -> None:
        self.apply_widget_set(self.__menu)

    def __start_gameplay(self, map: Map) -> None:
        Pausing(map.player.player, self.__pause_game)
        self.__state_machine.change_state(State.Explore, map)

    def __end_of_gameplay(self) -> None:
        self.switch_to_menu(None)

    def __won_tutorial(self) -> None:
        print("adfasdf")
        self.switch_to_menu(None)
        bell = ColorConfig.highlight_word("Bell")
        Popup.message("You won!", f"Congratulations, you defeated {bell} and successfully played the Tutorial!")

    def __start_fight(self, player: PlayerActor, enemy: Enemy, direction: Direction) -> None:
        self.__state_machine.change_state(State.Fight, (enemy, player))

    def __start_boss_fight(self, player: PlayerActor, boss: Boss, direction: Direction):
        self.__state_machine.change_state(State.BossFight, (player, boss))

    def switch_to_pause(self, data: PlayerActor) -> None:
        if data is not None:
            player = data
            self.__pause.set_data(player)
        self.apply_widget_set(self.__pause)

    def __pause_game(self, player: PlayerActor) -> None:
        self.__state_machine.change_state(State.Pause, player)

    def switch_to_explore(self, data) -> None:
        if data is not None:
            map = data
            self.__explore.set_data(map, map.player)
        self.apply_widget_set(self.__explore)

    def __continue_explore(self) -> None:
        self.__state_machine.change_state(State.Explore, None)

    def switch_to_fight(self, data) -> None:
        if data is not None:
            enemy = data[0]
            player = data[1]
            self.__fight.set_data(player, enemy)
        self.apply_widget_set(self.__fight)

    def switch_to_boss_fight(self, data) -> None:
        if data is not None:
            player = data[0]
            boss = data[1]
            self.__boss_fight.set_data(player, boss)
        self.apply_widget_set(self.__boss_fight)

    def __open_riddle(self, player: PlayerActor, riddle: Riddle):
        self.__state_machine.change_state(State.Riddle, (player, riddle))

    def switch_to_riddle(self, data) -> None:
        if data is not None:
            player = data[0]
            riddle = data[1]
            self.__riddle.set_data(player, riddle)
        self.apply_widget_set(self.__riddle)

    def __visit_shop(self, player: PlayerActor, items: "list of ShopItems"):
        self.__state_machine.change_state(State.Shop, (player, items))

    def switch_to_shop(self, data) -> None:
        if data is not None:
            player = data[0]
            items = data[1]
            self.__shop.set_data(player, items)
        self.apply_widget_set(self.__shop)

    def render(self) -> None:
        self.__cur_widget_set.render()

    def __use_menu_selection(self) -> None:
        if self.__menu.selection.use() and self.__cur_widget_set is self.__menu:
            self.render()

    def __pause_choices(self) -> None:
        if self.__pause.choices.use() and self.__cur_widget_set is self.__pause:
            self.move_focus(self.__pause.details.widget, auto_press_buttons=False)
            self.__pause.choices.render()
            self.__pause.details.render()

    def __pause_details(self) -> None:
        if self.__pause.details.use() and self.__cur_widget_set is self.__pause:
            self.move_focus(self.__pause.choices.widget, auto_press_buttons=False)
            self.__pause.details.render_reset()
            self.__pause.render()

    def __fight_choices(self) -> None:
        if self.__fight.choices.use() and self.__cur_widget_set is self.__fight:
            self.move_focus(self.__fight.details.widget, auto_press_buttons=False)
            self.__fight.choices.render()
            self.__fight.details.render()

    def __fight_details(self) -> None:
        if self.__fight.details.use() and self.__cur_widget_set is self.__fight:
            self.move_focus(self.__fight.choices.widget, auto_press_buttons=False)
            self.__fight.details.render_reset()
            self.__fight.render()   # needed for updating the StateVectors and the circuit

    def __boss_fight_choices(self) -> None:
        if self.__boss_fight.choices.use() and self.__cur_widget_set is self.__boss_fight:
            self.move_focus(self.__boss_fight.details.widget, auto_press_buttons=False)
            self.__boss_fight.choices.render()
            self.__boss_fight.details.render()

    def __boss_fight_details(self) -> None:
        if self.__boss_fight.details.use() and self.__cur_widget_set is self.__boss_fight:
            self.move_focus(self.__boss_fight.choices.widget, auto_press_buttons=False)
            self.__boss_fight.details.render_reset()
            self.__boss_fight.render()   # needed for updating the StateVectors and the circuit

    def __riddle_choices(self):
        if self.__riddle.choices.use() and self.__cur_widget_set is self.__riddle:
            self.move_focus(self.__riddle.details.widget, auto_press_buttons=False)
            self.__riddle.choices.render()
            self.__riddle.details.render()

    def __riddle_details(self) -> None:
        if self.__riddle.details.use() and self.__cur_widget_set is self.__riddle:
            self.move_focus(self.__riddle.choices.widget, auto_press_buttons=False)
            self.__riddle.details.render_reset()
            self.__riddle.render()   # needed for updating the StateVectors and the circuit

    def __shop_inventory(self) -> None:
        if self.__shop.inventory.use() and self.__cur_widget_set is self.__shop:
            self.move_focus(self.__shop.buy.widget, auto_press_buttons=False)
            self.__shop.render()

    def __shop_buy(self) -> None:
        if self.__shop.buy.use() and self.__cur_widget_set is self.__shop:
            self.move_focus(self.__shop.inventory.widget, auto_press_buttons=False)
            self.__shop.details.render_reset()
            self.__shop.buy.render_reset()
            self.__shop.buy.clear_text()
            self.__shop.render()


class State(Enum):
    Menu = 0
    Pause = 1
    Explore = 2
    Fight = 3
    Shop = 4
    Riddle = 5
    BossFight = 6


class StateMachine:
    def __init__(self, renderer: QrogueCUI):
        self.__renderer = renderer
        self.__cur_state = None
        self.__prev_state = None

    @property
    def cur_state(self) -> State:
        return self.__cur_state

    @property
    def prev_state(self) -> State:
        return self.__prev_state

    def change_state(self, state: State, data) -> None:
        self.__prev_state = self.__cur_state
        self.__cur_state = state

        if self.__cur_state == State.Menu:
            self.__renderer.switch_to_menu(data)
        elif self.__cur_state == State.Explore:
            self.__renderer.switch_to_explore(data)
        elif self.__cur_state == State.Fight:
            self.__renderer.switch_to_fight(data)
        elif self.__cur_state == State.Riddle:
            self.__renderer.switch_to_riddle(data)
        elif self.__cur_state == State.Shop:
            self.__renderer.switch_to_shop(data)
        elif self.__cur_state == State.BossFight:
            self.__renderer.switch_to_boss_fight(data)
        elif self.__cur_state == State.Pause:
            self.__renderer.switch_to_pause(data)
