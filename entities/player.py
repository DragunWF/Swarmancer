from components.transform import Transform

class Player:
    def __init__(self, x: float, y: float):
        self.transform = Transform(x, y)
        self.is_player = True
