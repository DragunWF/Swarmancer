class RangedAttack:
    def __init__(self, fire_rate: float = 1.0, attack_range: float = 150.0, projectile_speed: float = 300.0):
        self.fire_rate = fire_rate
        self.cooldown_timer = 0.0
        self.attack_range = attack_range
        self.projectile_speed = projectile_speed

class PlagueCaster:
    def __init__(self, cooldown: float = 3.0, blast_radius: float = 80.0, attack_range: float = 150.0, projectile_speed: float = 300.0):
        self.cooldown = cooldown
        self.cooldown_timer = 0.0
        self.blast_radius = blast_radius
        self.attack_range = attack_range
        self.projectile_speed = projectile_speed
