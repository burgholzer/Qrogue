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
    ERROR_COLOR = py_cui.RED_ON_BLUE
    TEXT_HIGHLIGHT = "/"
    CODE_WIDTH = 2
    TILE_HIGHLIGHT = "01"
    OBJECT_HIGHLIGHT = "02"
    WORD_HIGHLIGHT = "03"
    KEY_HIGHLIGHT = "04"
    __DIC = {
        TILE_HIGHLIGHT: py_cui.WHITE_ON_BLACK,
        OBJECT_HIGHLIGHT: py_cui.BLUE_ON_WHITE,
        WORD_HIGHLIGHT: py_cui.RED_ON_WHITE,
        KEY_HIGHLIGHT: py_cui.MAGENTA_ON_WHITE,
    }

    @staticmethod
    def is_number(text: str) -> bool:
        try:
            int(text)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_punctuation(char: str) -> bool:
        return char in [".", ",", "!", "?", ":", "\""]

    @staticmethod
    def count_meta_characters(paragraph: str, width: int, logger) -> int:
        """
        Counts how many meta characters (i.e. not printed characters) there are in the first #width characters of
        paragraph. This way we know for example by how much we can extend the rendered text since these characters
        won't be rendered.

        :param paragraph: the str we won't to count the number of meta characters for
        :param width: number of characters we consider in paragraph (i.e. line width)
        :param logger: logs potential errors
        :return: number of found meta characters
        """
        character_removals = 0
        # check how many meta-characters (indicating color rules) we have in our line
        highlight_index = paragraph.find(ColorConfig.TEXT_HIGHLIGHT, 0, width)
        start = True    # whether we search for the start of a highlighted section or an end
        while highlight_index > -1:
            highlight_index += 1
            if start:
                if highlight_index + ColorConfig.CODE_WIDTH <= len(paragraph) and \
                        ColorConfig.is_number(paragraph[highlight_index:highlight_index + ColorConfig.CODE_WIDTH]):
                    last_whitespace = paragraph.rfind(" ", highlight_index,
                                                      width + character_removals + 1 + ColorConfig.CODE_WIDTH)
                    if last_whitespace > -1:
                        character_removals += 1 + ColorConfig.CODE_WIDTH
                        start = False
                    elif paragraph[-1] == ColorConfig.TEXT_HIGHLIGHT:
                        # due to splitting a line in the middle of a color rule it can happen that there is no " "
                        # at the end but a "/" and therefore it would still fit
                        character_removals += 1 + ColorConfig.CODE_WIDTH + 1
                        break
                    elif ColorConfig.is_punctuation(paragraph[-1]): # TODO I don't think -1 is correct, because it is
                                                                    # todo the very end, but somehow it works
                        # if the very last word is highlighted we also have no whitespace at the end
                        character_removals += 1 + ColorConfig.CODE_WIDTH + 1
                        break
                    else:
                        break
                else:
                    logger.error(f"Illegal start index = {highlight_index} for \"{paragraph}\"")
            else:
                character_removals += 1
                start = True
            highlight_index = paragraph.find(ColorConfig.TEXT_HIGHLIGHT, highlight_index, width + character_removals)
        return character_removals

    @staticmethod
    def __highlight(type: str, text) -> str:
        return f"{ColorConfig.TEXT_HIGHLIGHT}{type}{text}{ColorConfig.TEXT_HIGHLIGHT}"

    @staticmethod
    def highlight_tile(tile: str) -> str:
        """
        Highlights tile strings.
        :param tile:
        :return:
        """
        return ColorConfig.__highlight(ColorConfig.TILE_HIGHLIGHT, tile)

    @staticmethod
    def highlight_object(obj: str) -> str:
        """
        Highlights something directly gameplay related. I.e. things you encounter in the game.
        :param obj:
        :return:
        """
        return ColorConfig.__highlight(ColorConfig.OBJECT_HIGHLIGHT, obj)

    @staticmethod
    def highlight_word(word: str) -> str:
        """
        Highlights special words that explain gameplay but are not encountered in the game themselves.
        :param word:
        :return:
        """
        return ColorConfig.__highlight(ColorConfig.WORD_HIGHLIGHT, word)

    @staticmethod
    def highlight_key(key: str) -> str:
        """
        Highlights a keyboard input.
        :param key:
        :return:
        """
        return ColorConfig.__highlight(ColorConfig.KEY_HIGHLIGHT, key)

    @staticmethod
    def get(char: str):
        try:
            return ColorConfig.__DIC[char]
        except KeyError:
            return ColorConfig.ERROR_COLOR


class PopupConfig:
    @staticmethod
    def default_color() -> int:
        return py_cui.BLACK_ON_WHITE
