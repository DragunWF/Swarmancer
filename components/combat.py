class RangedAttack:
    def __init__(self, fire_rate: float = 1.0, attack_range: float = 150.0, projectile_speed: float = 300.0):
        self.fire_rate = fire_rate
        self.cooldown_timer = 0.0
        self.attack_range = attack_range
        self.projectile_speed = projectile_speed
