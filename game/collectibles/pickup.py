
from game.collectibles.collectible import Collectible, CollectibleType


class Coin(Collectible):
    def __init__(self, amount: int = 1):
        super().__init__(CollectibleType.Coin)
        self.__amount = amount

    @property
    def amount(self):
        return self.__amount

    def name(self) -> str:
        return "Coin"

    def description(self) -> str:
        return "Coins are used to buy Collectibles from the Shop"

    def __str__(self):
        return f"{self.__amount}$"


class Key(Collectible):
    def __init__(self, amount: int = 1):
        super().__init__(CollectibleType.Key)
        self.__amount = amount

    @property
    def amount(self):
        return self.__amount

    def name(self) -> str:
        return "Key"

    def description(self) -> str:
        return "A Key is useful for opening locked doors."

    def __str__(self):
        return f"{self.__amount} key(s)"
