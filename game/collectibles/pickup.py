from abc import ABC

from game.collectibles.collectible import Collectible, CollectibleType, ShopItem


class Pickup(Collectible, ABC):
    __DEFAULT_PRICE = 5 * ShopItem.base_unit()

    def __init__(self, amount: int):
        super(Pickup, self).__init__(CollectibleType.Pickup)
        if amount <= 0:
            amount = 1
        self._amount = amount

    @property
    def amount(self):
        return self._amount

    def default_price(self) -> int:
        # the higher the amount the less the additional price (based on harmonic numbers)
        return int(sum([Pickup.__DEFAULT_PRICE / (i+1) for i in range(self._amount)]))


class Coin(Pickup):
    def __init__(self, amount: int = 1):
        super().__init__(amount)

    def name(self) -> str:
        return "Coin"

    def description(self) -> str:
        return "Coins are used to buy Collectibles from the Shop"

    def to_string(self):
        return f"{self.amount}$"

    def __str__(self) -> str:
        return self.to_string()


class Key(Pickup):
    def __init__(self, amount: int = 1):
        super().__init__(amount)

    def name(self) -> str:
        return "Key"

    def description(self) -> str:
        return "A Key is useful for opening locked doors."

    def to_string(self):
        return f"{self.amount} key(s)"

    def __str__(self) -> str:
        return self.to_string()


class Heart(Pickup):
    __PRICE_MULTIPLIER = 0.65   # hearts are a bit cheaper

    def __init__(self, amount: int = 1):
        super().__init__(amount)

    def name(self) -> str:
        return "Heart"

    def description(self) -> str:
        return "A Heart gives you back some of your HP."

    def default_price(self) -> int:
        return round(Heart.__PRICE_MULTIPLIER * super(Heart, self).default_price())

    def to_string(self) -> str:
        return f"Heart ({self.amount} HP)"

    def __str__(self) -> str:
        return self.to_string()


class Energy(Pickup):
    def __init__(self, amount: int = 10):
        super().__init__(amount)

    def name(self) -> str:
        return "Energy"

    def description(self) -> str:
        return "Gives back some energy to the robot so it can stay longer in a dungeon."

    def to_string(self) -> str:
        return f"Energy ({self.amount})"

    def __str__(self) -> str:
        return self.to_string()