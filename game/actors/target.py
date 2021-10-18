from abc import ABC, abstractmethod

from game.collectibles.collectible import Collectible
from game.logic.qubit import StateVector


class Target(ABC):
    def __init__(self, target: StateVector, reward: Collectible):
        self.__target = target
        self.__reward = reward
        self.__is_active = True

    @property
    def statevector(self) -> StateVector:
        return self.__target

    @property
    def is_active(self) -> bool:
        return self.__is_active

    def get_reward(self) -> Collectible:
        if self.is_active:
            self.__is_active = False
            temp = self.__reward
            self.__reward = None
            return temp
        return None

    def is_reached(self, state_vector: StateVector) -> bool:
        if self.__target.is_equal_to(state_vector):
            self._on_reached()
            return True
        return False

    def _on_reached(self):
        pass
