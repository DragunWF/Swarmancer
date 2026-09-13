from enum import Enum, auto

class GameState(Enum):
    PLAYING = auto()
    SHOP = auto()
    MENU = auto()
    DYING = auto()
    GAME_OVER = auto()
    PAUSED = auto()
    VICTORY = auto()
