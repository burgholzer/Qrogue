
from py_cui.widgets import BlockLabel


class Logger:
    __instance = None

    def __init__(self):
        if Logger.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.__label = None
            self.__info_counter = 0
            self.__text = ""
            Logger.__instance = self

    def set_label(self, label: BlockLabel):
        self.__label = label
        self.print("", clear=False)  # update the text of the newly set label

    def info(self, message):
        self.__info_counter += 1

    def error(self, message):
        self.println(f"ERROR! {message}", clear=False)

    def print(self, message: str, clear: bool = False):
        print(message)
        if clear:
            self.__text = message
        else:
            self.__text += message
        if self.__label is not None:
            self.__label.set_title(self.__text)

    def println(self, message: str = "", clear: bool = False):
        self.print(f"{message}\n", clear)

    def print_list(self, list=[], delimiter: str = ", "):
        sb = "["
        for elem in list:
            if elem is not None:
                sb += str(elem)
            sb += delimiter
        sb += "]"
        self.print(sb)

    def clear(self):
        self.__text = ""
        self.print("")

    @staticmethod
    def instance() -> "Logger":
        if Logger.__instance is None:
            raise Exception("This singleton has not been initialized yet!")
        return Logger.__instance
