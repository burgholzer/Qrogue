from game.actors.factory import EnemyFactory, FightDifficulty
from game.actors.enemy import Enemy as EnemyActor
from game.actors.boss import Boss as BossActor
from game.actors.player import Player as PlayerActor
from game.callbacks import OnWalkCallback
from game.collectibles.collectible import ShopItem
from game.collectibles.pickup import Coin, Key
from game.logic.qubit import StateVector
from game.map import tiles
from game.map.navigation import Coordinate, Direction
from game.map.rooms import Room, SpawnRoom, GateRoom, WildRoom, BossRoom, ShopRoom
from game.map.tiles import Door

from widgets.my_popups import Popup, CommonPopups


class TutorialDifficulty(FightDifficulty):
    def __init__(self):
        super().__init__(2, [Coin(3)])


class TutorialEnemy(EnemyActor):
    def __init__(self, target: StateVector, reward: tiles.Collectible):
        super().__init__(target, reward)

    def get_img(self):
        return "E"


class TutorialBoss(BossActor):
    def __init__(self):
        target = StateVector([0, 0, 0, 1, 0, 0, 0, 0])
        super().__init__(target, Coin(11))

    def get_img(self):
        return "B"


class TutorialEnemyFactory(EnemyFactory):
    def __init__(self, start_fight_callback: OnWalkCallback):
        self.__difficulty = TutorialDifficulty()
        super().__init__(start_fight_callback, self.__difficulty)

        self.__reward_index = 0
        self.__rewards = [
            Coin(3), Key(), Coin(2), Coin(1), Coin(5),
            Coin(), Key(),
        ]

    def get_enemy(self, player: PlayerActor) -> EnemyActor:
        stv = self.__difficulty.create_statevector(player)
        enemy = TutorialEnemy(stv, self.__rewards[self.__reward_index])
        self.__reward_index = (self.__reward_index + 1) % len(self.__rewards)
        return enemy


class TutorialTile(tiles.Message):
    def __init__(self, popup: Popup, id: int, is_active_callback: "bool(int)", progress_callback: "()" = None,
                 blocks: bool = False):
        super().__init__(popup, popup_times=1)
        self.__id = id
        self.__is_active = is_active_callback
        self.__progress = progress_callback
        self.__blocks = blocks

    def get_img(self):
        if self.is_active():
            return super(TutorialTile, self).get_img()
        else:
            return " "

    def is_walkable(self, direction: Direction, player: PlayerActor) -> bool:
        if self.__blocks:
            if self.is_active():
                return super(TutorialTile, self).is_walkable(direction, player)
            else:
                CommonPopups.TutorialBlocked.show()
                return False
        return super(TutorialTile, self).is_walkable(direction, player)

    def on_walk(self, direction: Direction, player: PlayerActor) -> None:
        if self.is_active():
            super(TutorialTile, self).on_walk(direction, player)
            self.__blocks = False # TutorialTiles should no longer affect the Player after they were activated
            if self.__progress is not None:
                self.__progress()

    def is_active(self):
        return self.__is_active(self.__id)


class CustomWildRoom(Room):
    def __init__(self, start_fight_callback: "void(EnemyActor, Direction, PlayerActor)",
                 tutorial_tile: TutorialTile, blocking_tile: TutorialTile):
        factory = TutorialEnemyFactory(start_fight_callback)
        self.__enemies = []
        for i in range(Room.INNER_WIDTH):
            self.__enemies.append(tiles.Enemy(factory, self.get_entangled_tiles, id=1, amplitude=1))
        tile_dic = {
            Coordinate(Room.MID_X - 1, 0): tutorial_tile,
            Coordinate(Room.INNER_WIDTH - 2, 2): tiles.Enemy(factory, self.get_entangled_tiles, id=0, amplitude=0),
            Coordinate(0, 3): tiles.Enemy(factory, self.get_entangled_tiles, id=0, amplitude=1),
            Coordinate(Room.MID_X - 1, Room.INNER_HEIGHT - 1): blocking_tile
        }
        for i in range(len(self.__enemies)):
            tile_dic[Coordinate(i, 1)] = self.__enemies[i]
        tile_list = Room.dic_to_tile_list(tile_dic)
        super().__init__(tile_list, north_door=True, south_door=tiles.Door(Direction.South))

    def get_entangled_tiles(self, id: int) -> "list of EnemyTiles":
        if id == 0:
            return []
        return self.__enemies

    def __str__(self):
        return "cWR"


class TutorialGateRoom(GateRoom):
    def __init__(self, tutorial_tile):
        tile_dic = {
            Coordinate(0, Room.MID_Y - 1): tutorial_tile
        }
        super().__init__(Door(Direction.West), tile_dic)


class Tutorial:
    def __init__(self):
        self.__cur_id = 0

    def is_active(self, id: int) -> bool:
        return self.__cur_id == id

    def should_block(self, id: int) -> bool:
        return self.__cur_id > id

    def progress(self):
        self.__cur_id += 1

    def create_tutorial_map(self, player: tiles.Player, start_fight_callback: "void(Player, Enemy, Direction)",
                            visit_shop_callback: "void(Player, list of ShopItems") -> "Room[][], Coordinate":
        messages = [
            "Great! The room you're about to enter gives you a new Gate you can use for your circuits. But it seems to "
            "be locked...",

            "Beware! Down there in the next room are some wild Enemies. Oh, maybe one of them has a key?",

            "Here they are! The number indicates the group they belong to. In a group their behaviour is entangled: "
            "If one member runs away when you challenge them, all others will too. But if they decide to fight you...\n"
            "Well, luckily the 0s are different. They are in no group and only care about themselves.\n"
            "Now go ahead and challenge an Enemy by stepping onto it.",

            "Nice! Next step onto the \"c\" and collect your new Gate.\n"
            "Afterwards go down to the room you haven't visited yet.",

            "Alright, now comes a room with real Enemies. Remember what I told you about the groups if you want "
            "to survive!\nTo the West of the next room waits the Boss, in the South is the Shop and West a Riddle "
            "that gives you a nice reward if you can solve it.\nGood Luck!",
        ]
        popups = [Popup(f"Tutorial #{i + 1}", messages[i], show=False)
                  for i in range(len(messages))]

        spawn_dic = {
            Coordinate(Room.INNER_WIDTH - 1, Room.MID_Y - 1): TutorialTile(popups[0], 0, self.is_active, self.progress),
            Coordinate(Room.MID_X - 1, Room.INNER_HEIGHT - 1): TutorialTile(popups[1], 1, self.is_active, self.progress,
                                                                            blocks=True)
        }
        spawn = SpawnRoom(player, spawn_dic, east_door=tiles.Door(Direction.East, locked=False),
                          south_door=tiles.Door(Direction.South))
        spawn_x = 1
        spawn_y = 0
        width = 5
        height = 5
        factory = TutorialEnemyFactory(start_fight_callback)

        rooms = [[None for x in range(width)] for y in range(height)]
        rooms[spawn_y][spawn_x] = spawn
        rooms[1][1] = CustomWildRoom(start_fight_callback, TutorialTile(popups[2], 2, self.is_active, self.progress),
                                     TutorialTile(popups[4], 4, self.is_active, self.progress, blocks=True))
        rooms[0][2] = TutorialGateRoom(TutorialTile(popups[3], 3, self.is_active, self.progress))   # TODO second tutorial tile for going back!!!!
        rooms[2][1] = WildRoom(factory, north_door=True, west_door=True, east_door=tiles.Door(Direction.East))
        rooms[2][2] = BossRoom(tiles.Door(Direction.West), tiles.Boss(TutorialBoss(), start_fight_callback))

        rooms[0][2] = ShopRoom(Door(Direction.West), [ShopItem(Key(2), 3), ShopItem(Key(1), 2)], visit_shop_callback)

        return rooms, Coordinate(spawn_x, spawn_y)
