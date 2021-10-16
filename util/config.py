import py_cui


class MapConfig:
    @staticmethod
    def tutorial_seed() -> int:
        return 0


class PopupConfig:
    @staticmethod
    def default_color() -> int:
        return py_cui.WHITE_ON_CYAN
