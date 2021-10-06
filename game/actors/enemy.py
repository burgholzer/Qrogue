from abc import ABC, abstractmethod

from game.actors.player import Player
from game.collectibles.collectible import Collectible
from game.collectibles.pickup import Coin
from game.logic.qubit import StateVector


class Enemy(ABC):
    def __init__(self, target: StateVector, reward: Collectible):
        self.__target = target
        self.__reward = reward
        self.__alive = True

    @abstractmethod
    def get_img(self):
        pass

    def _on_death(self) -> Collectible:
        self.__alive = False
        return self.__reward

    def get_statevector(self) -> StateVector:
        return self.__target

    def damage(self, state_vec: StateVector) -> (bool, Collectible):
        if self.__target.is_equal_to(state_vec):
            return True, self._on_death()
        return False, None

    def is_alive(self):
        return self.__alive

    def __str__(self):
        string = "Enemy ["
        for q in self.__target.to_value():
            string += f"{q} "
        string += "]"
        return string


class DummyEnemy(Enemy):
    def __init__(self, target: StateVector):
        super(DummyEnemy, self).__init__(target, Coin(1))

    def get_img(self):
        return "E"
