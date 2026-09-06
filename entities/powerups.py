from components.transform import Transform
from components.graphics import Graphics
from components.collider import Collider
from components.timers import LifespanTimer
from components.value import Value

class Resource:
    yield_amount = 3

    def __init__(self, x: float, y: float, yield_amount: int = None):
        self.transform = Transform(x, y)
        self.graphics = Graphics(color=(100, 255, 100), scale=6.0) # glowing green grave
        self.collider = Collider(radius=6.0, is_trigger=True)
        self.yield_amount = yield_amount if yield_amount is not None else Resource.yield_amount
        self.marked_for_deletion = False

class SoulPickup:
    def __init__(self, x: float, y: float):
        self.transform = Transform(x, y)
        self.graphics = Graphics(color=(0, 255, 255), scale=4.0) # cyan
        self.collider = Collider(radius=8.0, is_trigger=True)
        self.lifespan_timer = LifespanTimer(duration=15.0)
        self.value = Value(soul_amount=1)
        self.marked_for_deletion = False

class CursedChalice:
    def __init__(self, x: float, y: float):
        self.transform = Transform(x, y)
        self.graphics = Graphics(color=(218, 165, 32), scale=8.0) # goldenrod
        self.collider = Collider(radius=12.0, is_trigger=True)
        self.lifespan_timer = LifespanTimer(duration=15.0)
        self.value = Value(soul_amount=50)
        self.marked_for_deletion = False
