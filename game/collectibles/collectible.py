from abc import ABC
from enum import Enum


class CollectibleType(Enum):
    Consumable = 1
    Gate = 2
    ActiveItem = 3
    PassiveItem = 4
    Coin = 5


class Collectible(ABC):
    def __init__(self, type: CollectibleType):
        self.__type = type

    @property
    def type(self):
        return self.__type
