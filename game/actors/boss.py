
from abc import abstractmethod
from game.actors.enemy import Enemy
from game.collectibles.pickup import Coin
from game.logic.qubit import StateVector


class Boss(Enemy):
    @abstractmethod
    def get_reward(self):
        pass


class DummyBoss(Boss):
    def __init__(self):
        stv = StateVector([1, 0, 0, 0, 0, 0, 0, 0])
        super(DummyBoss, self).__init__(stv, Coin(3))

    def get_img(self):
        return "B"

    def get_reward(self):
        print("TODO: give reward")
