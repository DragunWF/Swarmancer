from components.transform import Transform
from components.player_state import PlayerState
from components.timers import ScatterTimer

class Player:
    def __init__(self, x: float, y: float):
        self.transform = Transform(x, y)
        self.state = PlayerState()
        self.scatter_timer = ScatterTimer()
        self.is_player = True
