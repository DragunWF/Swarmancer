class ScatterTimer:
    def __init__(self, cooldown_duration: float = 3.0, scatter_duration: float = 0.35):
        self.current_time = 0.0
        self.cooldown_duration = cooldown_duration
        self.active_time = 0.0
        self.scatter_duration = scatter_duration
