from components.transform import Transform
from components.graphics import Graphics
from components.collider import Collider

class Resource:
    def __init__(self, x: float, y: float):
        self.transform = Transform(x, y)
        self.graphics = Graphics(color=(100, 255, 100), scale=6.0) # glowing green grave
        self.collider = Collider(radius=6.0, is_trigger=True)
        self.marked_for_deletion = False
