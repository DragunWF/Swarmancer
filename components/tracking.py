class TargetTracker:
    def __init__(self, target, speed: float = 200.0, spiral_factor: float = 1.0):
        self.target = target
        self.speed = speed
        self.spiral_factor = spiral_factor
