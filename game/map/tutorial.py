from game.actors.factory import EnemyFactory, FightDifficulty, DummyFightDifficulty
from game.actors.enemy import Enemy as EnemyActor
from game.actors.boss import Boss as BossActor
from game.actors.player import Player as PlayerActor, PlayerAttributes, Backpack
from game.actors.riddle import Riddle
from game.callbacks import OnWalkCallback
from game.collectibles.collectible import ShopItem
from game.collectibles.pickup import Coin, Key
from game.logic.instruction import CXGate, HGate, XGate
from game.logic.qubit import StateVector, DummyQubitSet
from game.map import tiles
from game.map.navigation import Coordinate, Direction
from game.map.rooms import Room, SpawnRoom, GateRoom, WildRoom, BossRoom, ShopRoom, RiddleRoom
from game.map.tiles import Door
from util.config import ColorConfig as CC

from widgets.my_popups import Popup, CommonPopups


class TutorialPlayer(PlayerActor):
    def __init__(self):
        super(TutorialPlayer, self).__init__(PlayerAttributes(DummyQubitSet()), Backpack(content=[HGate(), XGate()]))


class TutorialDifficulty(FightDifficulty):
    def __init__(self):
        super().__init__(2, [Coin(3)])


class TutorialEnemy(EnemyActor):
    def __init__(self, target: StateVector, reward: tiles.Collectible):
        super().__init__(target, reward, flee_chance=0.0)

    def get_img(self):
        return "E"


class TutorialRiddle(Riddle):
    def __init__(self):
        target = StateVector([1, 0, 0, 0])
        reward = CXGate()
        super().__init__(target, reward, attempts=7)


class TutorialBoss(BossActor):
    def __init__(self):
        target = StateVector([0.707 + 0j, 0, 0, 0.707 + 0j])
        super().__init__(target, Coin(11))

    def get_img(self):
        return "B"


class TutorialEnemyFactory(EnemyFactory):
    def __init__(self, start_fight_callback: OnWalkCallback):
        self.__difficulty = TutorialDifficulty()
        super().__init__(start_fight_callback, self.__difficulty)

        self.__reward_index = 0
        self.__enemy_data = [
            (StateVector([0, 0, 1, 0]), Coin(2)),
            (StateVector([0.707 + 0j, 0.707 + 0j, 0, 0]), Key()),
            (StateVector([0, 0, 1, 0]), Coin(1)),
            (StateVector([0.707 + 0j, 0, 0.707 + 0j, 0]), Coin(4)),
            (StateVector([0, 1, 0, 0]), Coin(3)),
            (StateVector([1, 0, 0, 0]), Coin(2)),
        ]

    def get_enemy(self, player: PlayerActor, flee_chance: float) -> EnemyActor:
        data = self.__enemy_data[self.__reward_index]
        enemy = TutorialEnemy(data[0], data[1])
        self.__reward_index = (self.__reward_index + 1) % len(self.__enemy_data)
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
            if self.__blocks:
                return "X"
            else:
                return self._invisible

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
            Coordinate(0, Room.MID_Y - 1): tutorial_tile,
            Coordinate(2, Room.INNER_HEIGHT - 2): tiles.Enemy(factory, self.get_entangled_tiles, id=0, amplitude=0),
            Coordinate(3, 0): tiles.Enemy(factory, self.get_entangled_tiles, id=0, amplitude=1),
            Coordinate(Room.INNER_WIDTH - 1, Room.MID_Y - 1): blocking_tile
        }
        for i in range(len(self.__enemies)):
            tile_dic[Coordinate(1, i)] = self.__enemies[i]
        tile_list = Room.dic_to_tile_list(tile_dic)
        super().__init__(tile_list, west_door=True, east_door=tiles.Door(Direction.East))

    def get_entangled_tiles(self, id: int) -> "list of EnemyTiles":
        if id == 0:
            return []
        return self.__enemies

    def __str__(self):
        return "cWR"


class TutorialGateRoom(GateRoom):
    def __init__(self, tutorial_tile):
        tile_dic = {
            Coordinate(Room.MID_X - 1, 0): tutorial_tile
        }
        super().__init__(Door(Direction.North), tile_dic)


class Tutorial:
    __QUANTUM_COMPUTING = CC.highlight_word("Quantum Computing")
    __QUANTUM_GATES = CC.highlight_object("Quantum Gates")
    __QUANTUM_CIRCUIT = CC.highlight_object("Quantum Circuit")
    __ENEMIES = CC.highlight_object("Enemies")
    __QUANTUM_STATE = CC.highlight_object("Quantum State")
    __SPECIAL_ROOMS = CC.highlight_object("Special Rooms")
    __BOSS = CC.highlight_object("Boss")
    __QUANTUM_ALGORITHM = CC.highlight_word("Quantum Algorithm")
    __ARROW_KEYS = CC.highlight_key("Arrow Keys")
    __DOOR = CC.highlight_object("Door")
    __DOOR_TILE = CC.highlight_tile("-")
    __TUTORIAL_TILE = CC.highlight_tile(".")
    __SPACE = CC.highlight_key("Space")
    WelcomeMessage = \
        f"Qrogue is a game about {__QUANTUM_COMPUTING}. You will explore " \
        f"Dungeons with the help of {__QUANTUM_GATES} you can use for your " \
        f"{__QUANTUM_CIRCUIT}. But you are not the only one in the Dungeons! " \
        f"There are {__ENEMIES} challenging you to reach a certain " \
        f"{__QUANTUM_STATE}. Your goal is to expand your library of " \
        f"{__QUANTUM_GATES} which are hidden in " \
        f"{__SPECIAL_ROOMS} in the Dungeon or guarded " \
        f"by a {__BOSS} - a special Enemy that wants to see a " \
        f"{__QUANTUM_ALGORITHM} from you...\n" \
        f"Now let's start! Try to move around with the {__ARROW_KEYS} and " \
        f"go to the {__DOOR} ({__DOOR_TILE}) at the bottom!" \
        f"\nThe fields with a {__TUTORIAL_TILE} will show you the next steps. " \
        f"Now close this dialog and start playing by pressing {__SPACE}."

    def __init__(self):
        self.__cur_id = 0
        self.__fight = None
        self.__showed_fight_tutorial = False
        self.__riddle = None
        self.__showed_riddle_tutorial = False
        self.__shop = None
        self.__showed_shop_tutorial = False

    def is_active(self, id: int) -> bool:
        return self.__cur_id == id

    def should_block(self, id: int) -> bool:
        return self.__cur_id > id

    def progress(self):
        self.__cur_id += 1

    def fight(self, player: PlayerActor, enemy: EnemyActor, direction: Direction):
        self.__fight(player, enemy, direction)
        w = [CC.highlight_word("Fight"), CC.highlight_word("1)"), CC.highlight_object("StateVectors"),
             CC.highlight_word("Difference"), CC.highlight_word("zero"), CC.highlight_word("win"),
             CC.highlight_word("2)"), CC.highlight_object("Circuit"), CC.highlight_object("Qubits"), "3)", "4)", "5)"]
        if not self.__showed_fight_tutorial:
            Popup(f"Tutorial: {w[0]}",
                  f"{w[1]} In the middle of the screen you see 3 {w[2]}. The left one (Current State) can be adapted by "
                  "you while the right one (Target State) is constant and depending on the Enemy you fight. Between "
                  f"those two you also see the {w[3]}: If it gets {w[4]} you {w[5]} the Fight!\n"
                  f"{w[6]} Underneath the StateVectors is your {w[7]}. Currently you have 2 {w[8]} (q0, q1) and no "
                  "Gates applied to them. The before mentioned Current State reflects the output (out) of your Circuit.\n"
                  "3) On the left you can choose the action you want to take: \n"
                  "Adapt - Change your Circuit with the Gates available to you (selection to the right)\n"
                  "Commit - Commit your changes and update your StateVector. If Difference is not zero you lose 1 HP.\n"
                  "Items - Use one of your Items to make the Fight easier (you don't have any Items yet!)\n"
                  "Flee - Try to flee from the Fight. This is chance based and you lose 1 HP if you fail to flee (Note:"
                  " for Tutorial purposes you cannot flee in this room!)\n"
                  "4) The bottom right depends on the action you chose on the left side. E.g. you can choose the Gates "
                  "you want to use in your Circuit.\n"
                  "5) Use your arrow keys to navigate between your available options at the bottom and press SPACE to "
                  "use one. Again, your goal now is to reach the Target State of the Enemy. If you succeed, you "
                  "will get a reward!")
            self.__showed_fight_tutorial = True

    def riddle(self, player: PlayerActor, riddle: Riddle):
        self.__riddle(player, riddle)
        riddles = CC.highlight_object("Riddles")
        fights = CC.highlight_object("Fights")
        state = CC.highlight_object("Target State")
        circuit = CC.highlight_object("Circuit")
        hp = CC.highlight_word("don't lose HP")
        attempt = CC.highlight_word("Attempt")
        vanishes = CC.highlight_word("vanishes")
        give_up = CC.highlight_word("\"Give up\"")
        if not self.__showed_riddle_tutorial:
            Popup("Tutorial: Riddle",
                  f"{riddles} are very similar to {fights}. You have a {state} you need to reach (Difference is zero) "
                  f"by adapting your {circuit}. The main difference is that you {hp} if you fail but instead an "
                  f"{attempt} for solving the Riddle. When you have no more Attempts the Riddle {vanishes} together "
                  "with its reward - which is usually much better than the rewards from Fights. Also fleeing (or in "
                  f"this case {give_up}) will always succeed but obviously cost you your current Attempt which is why "
                  "you are notified if you have no more Attempts left.")
            self.__showed_riddle_tutorial = True

    def shop(self, player: PlayerActor, items: "list of ShopItems"):
        self.__shop(player, items)
        shop = CC.highlight_object("Shop")
        coins = CC.highlight_object("Coins")
        collec = CC.highlight_object("Collectibles")
        list_ = CC.highlight_word("list")
        buy = CC.highlight_word("buy")
        keys = CC.highlight_key("Arrow Keys")
        space = CC.highlight_key("Space")
        details = CC.highlight_word("details")
        leave = CC.highlight_word("\"-Leave-\"")
        reenter = CC.highlight_word("re-enter")
        if not self.__showed_shop_tutorial:
            Popup("Tutorial: Shop",
                  f"In the {shop} you can use {coins} you got (e.g. from Fights) to buy various {collec}. On the "
                  f"left side is a {list_} of everything you can {buy}. Navigate as usual with your {keys} and select "
                  f"something with {space} to see more {details} on the right side. There you can also buy it.\n"
                  f"{leave} obviously makes you leave the {shop}. You can {reenter} it later as long as there is "
                  "stuff left to buy.")
            self.__showed_shop_tutorial = True

    def boss_fight(self, player: PlayerActor, enemy: EnemyActor, direction: Direction):
        self.__fight(player, enemy, direction)
        bell = CC.highlight_word("Bell, the Master of Entanglement")
        both0 = CC.highlight_word("both 0")
        both1 = CC.highlight_word("both 1")
        Popup("Tutorial: Boss Fight",
              f"Now it's getting serious! You are fighting against {bell}. For the State you need to reach to defeat "
              f"him your two Qubits will always have to be the same: either {both0} or {both1}\n\n"
              "Good luck!")

    def build_tutorial_map(self, player: tiles.Player, start_fight_callback: "void(Player, Enemy, Direction)",
                           open_riddle_callback: "void(Player, Riddle)",
                           visit_shop_callback: "void(Player, list of ShopItems") -> "Room[][], Coordinate":
        self.__fight = start_fight_callback
        self.__riddle = open_riddle_callback
        self.__shop = visit_shop_callback
        w = [CC.highlight_object("Gate"), CC.highlight_object("Circuit"), CC.highlight_word("locked"),
             CC.highlight_object("Enemies"), CC.highlight_object("Key"), CC.highlight_word("number"),
             CC.highlight_word("group"), CC.highlight_word("entangled"), CC.highlight_word("all others will too"),
             CC.highlight_word("zeros are different"), CC.highlight_word("no group"),
             CC.highlight_word("stepping onto it"), CC.highlight_tile("c"), CC.highlight_word("groups"),
             CC.highlight_object("Boss"), CC.highlight_object("Shop"), CC.highlight_object("Riddle")]
        enemy = CC.highlight_object("Enemy")
        messages = [
            f"Great! The room you're about to enter gives you a new {w[0]} you can use for your "
            f"{w[1]}. But it seems to be {w[2]}...",

            f"Beware! In the next room are some wild {w[3]}. Oh, but maybe one of them has a "
            f"{w[4]}?",

            f"Here they are! The {w[5]} indicates the {w[6]} they belong to. In a group their behaviour is {w[7]}: \n"
            f"If one member runs away when you challenge them, {w[8]}. But if they decide to fight you...\n"
            f"Well, luckily the {w[9]}. They are in {w[10]} and only care about themselves.\n"
            f"Now go ahead and challenge an {enemy} by {w[11]}.",

            f"Nice! Next step onto the {w[12]} and collect your new {w[0]}.\n"
            "Afterwards go to the rooms on the right you haven't visited yet.",

            f"Alright, now comes a room with real {w[3]}. Remember what you were told about the {w[13]} if you want "
            f"to survive!\n"
            f"To the West of the next room waits the {w[14]}, in the South is the {w[15]} and "
            f"North a {w[16]} that gives you a nice reward if you can solve it.\n"
            "Good Luck!",
        ]
        popups = [Popup(f"Tutorial #{i + 1}", messages[i], show=False)
                  for i in range(len(messages))]

        spawn_dic = {
            Coordinate(Room.MID_X - 1, Room.INNER_HEIGHT - 1): TutorialTile(popups[0], 0, self.is_active, self.progress),
            Coordinate(Room.INNER_WIDTH - 1, Room.MID_Y - 1): TutorialTile(popups[1], 1, self.is_active, self.progress,
                                                                            blocks=True)
        }
        spawn = SpawnRoom(player, spawn_dic, east_door=tiles.Door(Direction.East),
                          south_door=tiles.Door(Direction.South, locked=True))
        spawn_x = 0
        spawn_y = 1
        width = 5
        height = 5
        factory = EnemyFactory(start_fight_callback, DummyFightDifficulty())

        rooms = [[None for x in range(width)] for y in range(height)]
        rooms[spawn_y][spawn_x] = spawn
        rooms[1][1] = CustomWildRoom(self.fight, TutorialTile(popups[2], 2, self.is_active, self.progress),
                                     TutorialTile(popups[4], 4, self.is_active, self.progress, blocks=True))
        rooms[2][0] = TutorialGateRoom(TutorialTile(popups[3], 3, self.is_active, self.progress))
        rooms[1][2] = WildRoom(factory, chance=0.8, north_door=True, west_door=True,
                               east_door=tiles.Door(Direction.East), south_door=tiles.Door(Direction.South))
        rooms[0][2] = RiddleRoom(tiles.Door(Direction.South), TutorialRiddle(), self.riddle)
        rooms[2][2] = ShopRoom(Door(Direction.North), [ShopItem(Key(2), 3), ShopItem(Key(1), 2)], self.shop)
        entangled_east = tiles.EntangledDoor(Direction.East)
        entangled_south = tiles.EntangledDoor(Direction.South)
        tiles.EntangledDoor.entangle(entangled_east, entangled_south)
        rooms[1][3] = WildRoom(factory, chance=0.7, north_door=True, west_door=True, east_door=entangled_east,
                               south_door=entangled_south)
        rooms[0][3] = BossRoom(tiles.Door(Direction.South), tiles.Boss(TutorialBoss(), start_fight_callback))
        rooms[1][4] = WildRoom(factory, chance=0.5, west_door=True)
        rooms[2][3] = WildRoom(factory, chance=0.6, north_door=True)

        return rooms, Coordinate(spawn_x, spawn_y)
