import os

import py_cui


class PathConfig:
    @staticmethod
    def base_path(file_name: str = "") -> str:
        folder = os.path.join("Documents", "Studium", "Master", "3. Semester", "Qrogue")
        return "D:\\" + os.path.join(folder, file_name)

    @staticmethod
    def write(file_name: str, text: str, may_exist: bool = True, append: bool = False):
        path = PathConfig.base_path(file_name)
        mode = "x"
        if may_exist:
            if os.path.exists(path):
                mode = "w"
                if append:
                    mode = "a"
        file = open(path, mode)
        file.write(text)
        file.close()

    @staticmethod
    def delete(file_name):
        path = PathConfig.base_path(file_name)
        if os.path.exists(path):
            os.remove(path)


class MapConfig:
    @staticmethod
    def tutorial_seed() -> int:
        return 0


class ColorConfig:
    TEXT_HIGHLIGHT = "/"
    TILE_HIGHLIGHT = "01"
    OBJECT_HIGHLIGHT = "02"
    WORD_HIGHLIGHT = "03"
    __DIC = {
        TILE_HIGHLIGHT: py_cui.WHITE_ON_BLACK,
        OBJECT_HIGHLIGHT: py_cui.CYAN_ON_RED,
        WORD_HIGHLIGHT: py_cui.RED_ON_WHITE,
    }

    @staticmethod
    def highlight_tile(tile: str) -> str:
        return f"{ColorConfig.TEXT_HIGHLIGHT}{ColorConfig.TILE_HIGHLIGHT}{tile}{ColorConfig.TEXT_HIGHLIGHT}"

    @staticmethod
    def highlight_object(obj: str) -> str:
        return f"{ColorConfig.TEXT_HIGHLIGHT}{ColorConfig.OBJECT_HIGHLIGHT}{obj}{ColorConfig.TEXT_HIGHLIGHT}"

    @staticmethod
    def highlight_word(word: str) -> str:
        return f"{ColorConfig.TEXT_HIGHLIGHT}{ColorConfig.WORD_HIGHLIGHT}{word}{ColorConfig.TEXT_HIGHLIGHT}"

    @staticmethod
    def get(char: str):
        return ColorConfig.__DIC[char]


class PopupConfig:
    @staticmethod
    def default_color() -> int:
        return py_cui.BLACK_ON_WHITE
