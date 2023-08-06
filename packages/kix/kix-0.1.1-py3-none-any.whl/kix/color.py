
class Color:

    RED: str = "RED"
    BLUE: str = "BLUE"
    GREEN: str = "GREEN"
    YELLOW: str = "YELLOW"
    PURPLE: str = "PURPLE"
    BLACK: str = "BLACK"
    DEFAULT: str = "DEFAULT"

    _ESC_CHAR = ""  # This is not a blank char, this is a unicode /33.

    _COLOR_MAP = {
        RED: "[31m",
        GREEN: "[32m",
        YELLOW: "[33m",
        BLUE: "[34m",
        PURPLE: "[35m",
        BLACK: "[90m",
        DEFAULT: "[0m",
    }

    @classmethod
    def set_color(cls, key: str, content: str):
        start_color = Color._ESC_CHAR + cls._COLOR_MAP[key]
        end_color = Color._ESC_CHAR + cls._COLOR_MAP[cls.DEFAULT]
        return f"{start_color}{content}{end_color}"

    # ======================================================================================================================
    # Public Set Color Methods
    # ======================================================================================================================


def red(text: str) -> str:
    return Color.set_color(Color.RED, text)


def blue(text: str) -> str:
    return Color.set_color(Color.BLUE, text)


def green(text: str) -> str:
    return Color.set_color(Color.GREEN, text)


def yellow(text: str) -> str:
    return Color.set_color(Color.YELLOW, text)


def purple(text: str) -> str:
    return Color.set_color(Color.PURPLE, text)


def black(text: str) -> str:
    return Color.set_color(Color.BLACK, text)
