import random


class MyRandom:
    _MAX_SEED = 1000000000

    def __init__(self, seed: int):
        seed = seed % self._MAX_SEED
        self.__random = random.Random(seed)

    def get(self):
        return self.__random.random()

    def get_int(self, min: int = 0, max: int = _MAX_SEED) -> int:
        return min + int(self.get() * (max - min))

    def get_element(self, iterable, remove: bool = False):
        index = self.get_int(min=0, max=len(iterable))
        if remove:
            elem = iterable[index]
            iterable.remove(index)
            return elem
        else:
            return iterable[index]


class RandomManager(MyRandom):
    __instance = None

    def __init__(self, seed: int):
        if RandomManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super().__init__(seed)
            RandomManager.__instance = self

    def create_new(self) -> MyRandom:
        seed = self.get_int()
        return MyRandom(seed)

    @staticmethod
    def instance() -> "RandomManager":
        if RandomManager.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return RandomManager.__instance
