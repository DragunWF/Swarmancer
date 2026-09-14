class PlayerState:
    def __init__(self):
        self.is_dense = False
        self.has_skeletal_archers = False
        self.has_plague_wizard = False
        self.grave_robbers_yield_level = 0  # Tracks the purchased tier (0 = not purchased, 1–3 = active)
