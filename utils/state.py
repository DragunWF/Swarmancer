from enum import Enum, auto

class GameState(Enum):
    PLAYING = auto()
    SHOP = auto()
    MENU = auto()
    GAME_OVER = auto()
    PAUSED = auto()
    VICTORY = auto()
