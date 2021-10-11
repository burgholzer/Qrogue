from game.actors.factory import EnemyFactory, FightDifficulty
from game.actors.enemy import Enemy as EnemyActor
from game.actors.player import Player as PlayerActor
from game.callbacks import OnWalkCallback
from game.collectibles.pickup import Coin, Key
from game.logic.qubit import StateVector
from game.map.navigation import Coordinate, Direction
from game.map.rooms import Room

from game.map.tiles import Enemy as EnemyTile, Door, Collectible


class TutorialEnemy(EnemyActor):
    def __init__(self, target: StateVector, reward: Collectible):
        super().__init__(target, reward)

    def get_img(self):
        return "E"


class TutorialDifficulty(FightDifficulty):
    def __init__(self):
        super().__init__(2, [])


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


class CustomWildRoom(Room):
    def __init__(self, start_fight_callback: "void(EnemyActor, Direction, PlayerActor)"):
        factory = TutorialEnemyFactory(start_fight_callback)
        self.__enemies = []
        for i in range(Room.INNER_WIDTH):
            self.__enemies.append(EnemyTile(factory, self.get_entangled_tiles, id=1, amplitude=1))
        tile_dic = {
            Coordinate(Room.INNER_WIDTH-2, 2): EnemyTile(factory, self.get_entangled_tiles, id=0, amplitude=0),
            Coordinate(0, 3): EnemyTile(factory, self.get_entangled_tiles, id=0, amplitude=1),
        }
        for i in range(len(self.__enemies)):
            tile_dic[Coordinate(i, 1)] = self.__enemies[i]
        tile_list = Room.dic_to_tile_list(tile_dic)
        super().__init__(tile_list, north_door=True, south_door=Door(Direction.South))

    def get_entangled_tiles(self, id: int) -> "list of EnemyTiles":
        if id == 0:
            return []
        return self.__enemies

    def __str__(self):
        return "cWR"
