class PulsingAnimation:
    def __init__(self, speed: float = 2.0, amplitude: float = 0.1):
        self.time_elapsed = 0.0
        self.speed = speed
        self.amplitude = amplitude
