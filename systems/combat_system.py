from systems.system import System
from entities.projectiles import Projectile
from utils.spatial_hash import SpatialHash
from pygame.math import Vector2

class CombatSystem(System):
    def __init__(self):
        pass

    def update(self, entities, dt):
        archers = []
        enemies = []

        # Find archers and enemies
        for entity in entities:
            if hasattr(entity, 'ranged_attack') and hasattr(entity, 'transform'):
                archers.append(entity)
            if getattr(entity, 'is_enemy', False) and getattr(entity, 'enemy_type', None) == 'grunt' and hasattr(entity, 'transform'):
                enemies.append(entity)

        # Tick down cooldowns even if no enemies
        for archer in archers:
            if archer.ranged_attack.cooldown_timer > 0:
                archer.ranged_attack.cooldown_timer -= dt

        if not archers or not enemies:
            return

        # Build spatial hash for enemies
        spatial_hash = SpatialHash(150.0)
        for enemy in enemies:
            spatial_hash.insert(enemy, enemy.transform.x, enemy.transform.y)

        new_projectiles = []

        for archer in archers:
            ra = archer.ranged_attack
            if ra.cooldown_timer <= 0:
                archer_pos = Vector2(archer.transform.x, archer.transform.y)
                potential_targets = spatial_hash.query_radius(archer_pos.x, archer_pos.y, ra.attack_range)
                
                nearest_enemy = None
                min_dist_sq = ra.attack_range ** 2

                for target in potential_targets:
                    if getattr(target, 'is_enemy', False) and getattr(target, 'enemy_type', None) == 'grunt':
                        target_pos = Vector2(target.transform.x, target.transform.y)
                        dist_sq = archer_pos.distance_squared_to(target_pos)
                        if dist_sq < min_dist_sq:
                            min_dist_sq = dist_sq
                            nearest_enemy = target
                
                if nearest_enemy:
                    target_pos = Vector2(nearest_enemy.transform.x, nearest_enemy.transform.y)
                    direction = target_pos - archer_pos
                    if direction.length_squared() > 0:
                        direction = direction.normalize()
                        
                        proj = Projectile(
                            archer_pos.x, archer_pos.y, 
                            direction.x * ra.projectile_speed, 
                            direction.y * ra.projectile_speed
                        )
                        new_projectiles.append(proj)
                        ra.cooldown_timer = ra.fire_rate

        if new_projectiles:
            entities.extend(new_projectiles)
