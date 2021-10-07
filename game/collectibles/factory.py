from game.collectibles.collectible import Collectible
from game.logic.instruction import HGate, SwapGate
from util.my_random import RandomManager


class CollectibleFactory:
    def __init__(self, pool: "list of Collectibles") -> None:
        self.__pool = pool

    def produce(self) -> Collectible:
        return RandomManager.instance().get_element(self.__pool)


class GateFactories:
    @staticmethod
    def standard_factory():
        return CollectibleFactory(pool=[
            SwapGate(0, 1), SwapGate(1, 2), SwapGate(0, 2), SwapGate(2, 1)
        ])
