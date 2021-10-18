from abc import ABC, abstractmethod

from game.collectibles.collectible import Collectible
from game.logic.qubit import StateVector


class Enemy(ABC):
    def __init__(self, target: StateVector, reward: Collectible, flee_chance: float):
        self.__target = target
        self.__reward = reward
        self.__flee_chance = flee_chance
        self.__alive = True

    @property
    def flee_chance(self):
        return self.__flee_chance

    @abstractmethod
    def get_img(self):
        pass

    def _on_death(self) -> None:
        self.__alive = False

    def get_statevector(self) -> StateVector:
        return self.__target

    def get_reward(self) -> Collectible:
        if not self.is_alive():
            temp = self.__reward
            self.__reward = None
            return temp
        return None

    def damage(self, state_vec: StateVector) -> bool:
        if self.__target.is_equal_to(state_vec):
            self._on_death()
            return True
        return False

    def is_alive(self):
        return self.__alive

    def __str__(self):
        string = "Enemy ["
        for q in self.__target.to_value():
            string += f"{q} "
        string += "]"
        return string


class DummyEnemy(Enemy):
    def __init__(self, target: StateVector, reward: Collectible, flee_chance: float):
        super(DummyEnemy, self).__init__(target, reward, flee_chance)

    def get_img(self):
        return "E"
