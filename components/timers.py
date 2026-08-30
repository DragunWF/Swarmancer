class ScatterTimer:
    def __init__(self, cooldown_duration: float = 3.0, scatter_duration: float = 0.35):
        self.current_time = 0.0
        self.cooldown_duration = cooldown_duration
        self.active_time = 0.0
        self.scatter_duration = scatter_duration


class AimingTimer:
    def __init__(self, charge_duration: float = 2.5, fire_duration: float = 0.5):
        # --- Telegraph Phase ---
        self.charge_duration = charge_duration  # Total seconds before the laser fires
        self.elapsed = 0.0                      # Accumulates dt; written by behavior_system

        # --- Active Firing Phase ---
        self.is_firing = False                  # Flipped by behavior_system when elapsed >= charge_duration
        self.fire_duration = fire_duration      # How long the beam stays active
        self.fire_elapsed = 0.0                 # Accumulates during firing; reset resets the cycle


class FuseTimer:
    def __init__(self, duration: float = 5.0):
        # Total seconds before the Boomer self-detonates regardless of contact
        self.duration = duration
        # Accumulates dt each frame; written exclusively by behavior_system
        self.elapsed = 0.0


class LifespanTimer:
    def __init__(self, duration: float = 15.0):
        self.duration = duration
        self.elapsed = 0.0
