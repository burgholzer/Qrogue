
from abc import ABC, abstractmethod
from enum import Enum

import py_cui

from game.actors.boss import Boss as BossActor
from game.actors.factory import EnemyFactory
from game.actors.player import Player as PlayerActor
from game.callbacks import OnWalkCallback
from game.collectibles.factory import CollectibleFactory
from game.map.navigation import Direction
from util.logger import Logger
from util.my_random import RandomManager
from widgets.my_popups import Popup


class TileCode(Enum):
    Invalid = -1    # when an error occurs, e.g. a tile at a non-existing position should be retrieved
    Void = 7        # tile outside of the playable area
    Floor = 0       # simple floor tile without special meaning
    FogOfWar = 3    # tile of a place we cannot see yet
    Message = 6     # tile for displaying a popup message

    Wall = 1
    Obstacle = 2
    Door = 4

    Player = 20
    Enemy = 30
    Boss = 40

    Collectible = 50


class Tile(ABC):
    def __init__(self, code: TileCode):
        self.__code = code

    @property
    def code(self) -> TileCode:
        return self.__code

    @abstractmethod
    def get_img(self):
        pass

    @abstractmethod
    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        pass


class WalkTriggerTile(Tile):
    def __init__(self, code: TileCode):
        super().__init__(code)

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return True
    
    @abstractmethod
    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        """
        Event that is triggered when an actor moves onto this Tile
        :param direction: the Direction from which the actor moves onto this Tile
        :param player: the actor (e.g. Player) that is moving onto this Tile
        :return: None
        """
        pass


class Invalid(Tile):
    def __init__(self):
        super().__init__(TileCode.Invalid)

    def get_img(self):
        return "§"

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return False


class Void(Tile):
    def __init__(self):
        super().__init__(TileCode.Floor)

    def get_img(self):
        return " "

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return False


class Floor(Tile):
    def __init__(self):
        super().__init__(TileCode.Floor)

    def get_img(self):
        return " "

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return True


class Wall(Tile):
    def __init__(self):
        super().__init__(TileCode.Wall)

    def get_img(self):
        return "#"

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return False


class Obstacle(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    def get_img(self):
        return "o"

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return False


class FogOfWar(Tile):
    def __init__(self):
        super().__init__(TileCode.Obstacle)

    def get_img(self):
        return "~"

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return True


class Message(WalkTriggerTile):
    def __init__(self, popup: Popup, popup_times: int = 1):
        super().__init__(TileCode.Message)
        self.__popup = popup
        self.__times = popup_times

    def get_img(self):
        if self.__times > 0:
            return "."
        else:
            return " "

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return True

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        if self.__times > 0:
            self.__popup.show()
        self.__times -= 1


class Door(WalkTriggerTile):
    def __init__(self, direction: Direction, locked: bool = False, opened: bool = False):   # todo entangled door as extra class?
        super().__init__(TileCode.Door)
        self.__direction = direction
        self.__locked = locked
        self.__opened = opened

    def get_img(self):
        if self.__opened:
            return " "
        if self.__direction is Direction.East or self.__direction is Direction.West:
            return "|"
        else:
            return "-"

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        if direction == self.__direction or direction == self.__direction.opposite():
            if self.__locked:
                if player.key_count > 0:
                    return True
                else:
                    Logger.instance().println("Door is locked!", clear=True)
                    return False
            else:
                return True
        else:
            return False

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        if self.__locked and not player.use_key():
            Logger.instance().error(f"Error! walked on a door without having enough keys!\n#keys={player.key_count}"
                                    f", dir={direction}")
        else:
            self.__opened = True

    @property
    def direction(self) -> Direction:
        return self.__direction

    def unlock(self) -> None:   # todo
        self.__locked = False


class Collectible(WalkTriggerTile):
    def __init__(self, factory: CollectibleFactory):
        super().__init__(TileCode.Collectible)
        self.__factory = factory
        self.__active = True

    def get_img(self):
        if self.__active:
            return "c"
        else:
            return " "

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return True

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        if self.__active:
            player = player
            player.give_collectible(self.__factory.produce())
            self.__active = False


class Player(Tile):
    def __init__(self, player: PlayerActor):
        super().__init__(TileCode.Player)
        self.__player = player

    def get_img(self):
        return "P"

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        return True # todo check

    @property
    def player(self) -> PlayerActor:
        return self.__player


class _EnemyState(Enum):
    UNDECIDED = 0
    FREE = 1
    FIGHT = 2
    DEAD = 3
    FLED = 4
class Enemy(WalkTriggerTile):
    def __init__(self, factory: EnemyFactory, get_entangled_tiles,
                 id: int = 0, amplitude: float = 0.5):
        super().__init__(TileCode.Enemy)
        self.__factory = factory
        self.__state = _EnemyState.UNDECIDED
        self.__get_entangled_tiles = get_entangled_tiles
        self.__id = id
        self.__amplitude = amplitude

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        if isinstance(player, PlayerActor):
            if self.__state == _EnemyState.UNDECIDED:
                if self.measure():
                    enemy = self.__factory.get_enemy(player)
                    self.__factory.callback(player, enemy, direction)
                    self.__state = _EnemyState.DEAD
                else:
                    self.__state = _EnemyState.FLED
            elif self.__state == _EnemyState.FIGHT:
                enemy = self.__factory.get_enemy(player)
                self.__factory.callback(player, enemy, direction)
                self.__state = _EnemyState.DEAD
            elif self.__state == _EnemyState.FREE:
                self.__state = _EnemyState.FLED

    def get_img(self):
        if self.__state == _EnemyState.DEAD :
            return " "
        elif self.__state == _EnemyState.FLED:
            return " "
        else:
            return str(self.__id)

    @property
    def amplitude(self) -> float:
        return self.__amplitude

    def _set_state(self, val: _EnemyState) -> None:
        if self.__state == _EnemyState.UNDECIDED:
            self.__state = val
        else:
            raise RuntimeError("Illegal program state!")

    def measure(self):
        if 0 < self.__id <= 9:
            entangled_tiles = self.__get_entangled_tiles(self.__id)
        else:
            entangled_tiles = [self]

        state = _EnemyState.FREE
        if RandomManager.instance().get() < self.amplitude:
            state = _EnemyState.FIGHT
        for enemy in entangled_tiles:
            enemy._set_state(state)

        return state == _EnemyState.FIGHT


class Boss(WalkTriggerTile):
    def __init__(self, boss: BossActor, on_walk_callback: OnWalkCallback):
        super().__init__(TileCode.Boss)
        self.__boss = boss
        self.__on_walk_callback = on_walk_callback

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        self.__on_walk_callback(player, self.boss, direction)

    def get_img(self):
        return "B"

    @property
    def boss(self):
        return self.__boss


__color_manager = {
    TileCode.Invalid: py_cui.RED_ON_BLUE,
    TileCode.Void: py_cui.CYAN_ON_BLACK,
    TileCode.Floor: py_cui.CYAN_ON_BLACK,
    TileCode.Wall: py_cui.BLACK_ON_CYAN,
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
