class Collider:
    def __init__(self, radius: float, is_trigger: bool = False):
        self.radius = radius
        self.is_trigger = is_trigger
