from game.controls import Controls
from util.config import PathConfig
from util.logger import Logger


class GameSimulator:
    def __init__(self, controls: Controls, path: str, in_keylog_folder: bool = True):
        self.__controls = controls

        path = "12112021_202641.qrkl"
        self.__reader = PathConfig.read_keylog_buffered(path, in_keylog_folder)
        if self.__reader is None:
            Logger.instance().error("invalid path!")
        self.__cur_chunk = self.__next_chunk()
        self.__cur_index = -1

    def __next_chunk(self) -> bytes:
        try:
            chunk = next(self.__reader)
            self.__cur_index = -1
            return bytes(chunk, "utf-8")
        except StopIteration:
            return None

    def __next_key(self) -> int:
        """

        :return: the next key or -1 if we should retry (self.__cur_chunk is None if we reached the end)
        """
        self.__cur_index += 1
        if 0 <= self.__cur_index < len(self.__cur_chunk):
            code = self.__cur_chunk[self.__cur_index]
            key = self.__controls.decode(code)
            if key:
                return key
        else:
            self.__cur_chunk = self.__next_chunk()
        return -1

    def next(self) -> int:
        """

        :return: the key to press or None if the simulation finished
        """
        while self.__cur_chunk is not None:
            key = self.__next_key()
            if key > -1:
                return key
        return None
