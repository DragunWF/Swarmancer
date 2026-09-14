import random
import math
from utils.spatial_hash import SpatialHash
from entities.powerups import CursedChalice
from entities.powerups import SoulPickup
from utils.asset_loader import AssetLoader

class CollisionSystem:
    def __init__(self, on_resource_collected=None, on_currency_collected=None, on_entity_spawned=None, on_particle_spawned=None):
        self.on_resource_collected = on_resource_collected
        self.on_currency_collected = on_currency_collected
        self.on_entity_spawned = on_entity_spawned
        self.on_particle_spawned = on_particle_spawned

    def _try_drop_soul(self, x, y):
        if not self.on_entity_spawned:
            return
        roll = random.random()
        if roll < 0.01:
            self.on_entity_spawned(CursedChalice(x, y))
        elif roll < 0.20:
            self.on_entity_spawned(SoulPickup(x, y))

    def update(self, entities, dt):
        boids = [e for e in entities if hasattr(e, 'collider') and hasattr(e, 'physics') and not getattr(e, 'is_enemy', False) and e.__class__.__name__ not in ('Projectile', 'PlagueBomb')]
        resources = [e for e in entities if hasattr(e, 'collider') and hasattr(e, 'graphics') and hasattr(e, 'transform') and e.__class__.__name__ == 'Resource']
        enemies = [e for e in entities if getattr(e, 'is_enemy', False) and hasattr(e, 'collider')]
        projectiles = [e for e in entities if e.__class__.__name__ in ('Projectile', 'PlagueBomb')]
        player = next((e for e in entities if getattr(e, 'is_player', False)), None)


        # 150.0 covers max Boomer blast radius
        spatial_hash = SpatialHash(150.0)
        for boid in boids:
            spatial_hash.insert(boid, boid.transform.x, boid.transform.y)

        for resource in resources:
            if resource.marked_for_deletion:
                continue

            max_radius = resource.collider.radius + 15.0 # Assuming max boid radius is small (~15)
            potential_boids = spatial_hash.query_radius(resource.transform.x, resource.transform.y, max_radius)

            for boid in potential_boids:
                dx = boid.transform.x - resource.transform.x
                dy = boid.transform.y - resource.transform.y
                distance_sq = dx * dx + dy * dy
                
                radius_sum = boid.collider.radius + resource.collider.radius
                if distance_sq < radius_sum * radius_sum:
                    resource.marked_for_deletion = True
                    AssetLoader().play_sound("pickup")
                    if self.on_resource_collected:
                        self.on_resource_collected(resource)
                    break # One boid can collect it

        pickups = [e for e in entities if hasattr(e, 'collider') and hasattr(e, 'value') and not getattr(e, 'marked_for_deletion', False)]
        for pickup in pickups:
            max_radius = pickup.collider.radius + 15.0
            potential_boids = spatial_hash.query_radius(pickup.transform.x, pickup.transform.y, max_radius)
            for boid in potential_boids:
                if getattr(boid, 'marked_for_deletion', False):
                    continue
                dx = boid.transform.x - pickup.transform.x
                dy = boid.transform.y - pickup.transform.y
                distance_sq = dx * dx + dy * dy
                radius_sum = boid.collider.radius + pickup.collider.radius
                if distance_sq < radius_sum * radius_sum:
                    pickup.marked_for_deletion = True
                    AssetLoader().play_sound("pickup")
                    if self.on_currency_collected:
                        self.on_currency_collected(pickup.value.soul_amount, pickup.transform.x, pickup.transform.y)
                    break

        # 1-to-1 Attrition (Grunts only — Boomers use is_trigger and are handled below)
        for enemy in enemies:
            if getattr(enemy, 'marked_for_deletion', False):
                continue
            # Skip trigger-type colliders; they are processed in the AoE block
            if getattr(enemy, 'collider', None) and enemy.collider.is_trigger:
                continue
                
            max_radius = enemy.collider.radius + 15.0
            potential_boids = spatial_hash.query_radius(enemy.transform.x, enemy.transform.y, max_radius)
            
            for boid in potential_boids:
                if getattr(boid, 'marked_for_deletion', False):
                    continue
                dx = enemy.transform.x - boid.transform.x
                dy = enemy.transform.y - boid.transform.y
                distance_sq = dx * dx + dy * dy
                radius_sum = enemy.collider.radius + boid.collider.radius
                if distance_sq < radius_sum * radius_sum:
                    enemy.marked_for_deletion = True
                    boid.marked_for_deletion = True
                    self._try_drop_soul(enemy.transform.x, enemy.transform.y)
                    AssetLoader().play_sound("skeleton_pop")
                    if self.on_particle_spawned:
                        self.on_particle_spawned("skeleton_shatter", boid.transform.x, boid.transform.y)
                        self.on_particle_spawned("vanguard_pop", enemy.transform.x, enemy.transform.y)
                    break  # One enemy pops exactly one boid

        # --- Projectile Hit Detection ---
        for proj in projectiles:
            if getattr(proj, 'marked_for_deletion', False):
                continue
            for enemy in enemies:
                if getattr(enemy, 'marked_for_deletion', False):
                    continue
                dx = proj.transform.x - enemy.transform.x
                dy = proj.transform.y - enemy.transform.y
                distance_sq = dx * dx + dy * dy
                radius_sum = proj.collider.radius + enemy.collider.radius
                if distance_sq < radius_sum * radius_sum:
                    enemy.marked_for_deletion = True
                    proj.marked_for_deletion = True
                    self._try_drop_soul(enemy.transform.x, enemy.transform.y)
                    
                    if getattr(proj, 'projectile_type', None) == 'plague_bomb':
                        AssetLoader().play_sound("dwarf_explosion")
                        if self.on_particle_spawned:
                            self.on_particle_spawned("plague_detonation", proj.transform.x, proj.transform.y)
                            self.on_particle_spawned("vanguard_pop", enemy.transform.x, enemy.transform.y)
                            
                        # AoE Detonation
                        blast_radius_sq = proj.blast_radius * proj.blast_radius
                        for blast_enemy in enemies:
                            if getattr(blast_enemy, 'marked_for_deletion', False) or getattr(blast_enemy, 'enemy_type', None) != 'grunt':
                                continue
                            if blast_enemy == enemy:
                                continue # Already popped
                                
                            dx_b = proj.transform.x - blast_enemy.transform.x
                            dy_b = proj.transform.y - blast_enemy.transform.y
                            if (dx_b * dx_b + dy_b * dy_b) < blast_radius_sq:
                                blast_enemy.marked_for_deletion = True
                                self._try_drop_soul(blast_enemy.transform.x, blast_enemy.transform.y)
                                AssetLoader().play_sound("skeleton_pop")
                                if self.on_particle_spawned:
                                    self.on_particle_spawned("vanguard_pop", blast_enemy.transform.x, blast_enemy.transform.y)
                    else:
                        AssetLoader().play_sound("skeleton_pop")
                        if self.on_particle_spawned:
                            if getattr(enemy, 'enemy_type', None) == 'laser_drone':
                                self.on_particle_spawned("sun_wizard_death", enemy.transform.x, enemy.transform.y)
                            elif getattr(enemy, 'enemy_type', None) == 'boomer':
                                self.on_particle_spawned("sapper_detonation", enemy.transform.x, enemy.transform.y)
                            else:
                                self.on_particle_spawned("vanguard_pop", enemy.transform.x, enemy.transform.y)
                    break

        # --- Enemy Projectile Hit Detection ---
        enemy_projectiles = [e for e in entities if getattr(e, 'projectile_type', None) == 'solar_gold_bolt']
        for proj in enemy_projectiles:
            if getattr(proj, 'marked_for_deletion', False):
                continue
            
            max_radius = proj.collider.radius + 15.0
            potential_boids = spatial_hash.query_radius(proj.transform.x, proj.transform.y, max_radius)
            
            for boid in potential_boids:
                if getattr(boid, 'marked_for_deletion', False):
                    continue
                dx = proj.transform.x - boid.transform.x
                dy = proj.transform.y - boid.transform.y
                distance_sq = dx * dx + dy * dy
                radius_sum = proj.collider.radius + boid.collider.radius
                if distance_sq < radius_sum * radius_sum:
                    proj.marked_for_deletion = True
                    boid.marked_for_deletion = True
                    AssetLoader().play_sound("skeleton_pop")
                    if self.on_particle_spawned:
                        self.on_particle_spawned("skeleton_shatter", boid.transform.x, boid.transform.y)
                    break

        # --- Boomer AoE Detonation ---
        # Triggers when: (a) the Boomer's contact radius touches any boid, OR
        # (b) behavior_system has set fuse_expired = True after the fuse duration elapses.
        # Once triggered, every boid within blast_radius is destroyed. Punishes Dense state
        # implicitly — tightly packed swarms have more units within the blast footprint.
        boomers = [e for e in entities
                   if getattr(e, 'enemy_type', None) == 'boomer'
                   and not getattr(e, 'has_detonated', False)
                   and not getattr(e, 'marked_for_deletion', False)]

        for boomer in boomers:
            # Check contact trigger (Phase 1)
            contacted = False
            
            max_contact_radius = boomer.collider.radius + 15.0
            potential_contact_boids = spatial_hash.query_radius(boomer.transform.x, boomer.transform.y, max_contact_radius)
            
            for boid in potential_contact_boids:
                if getattr(boid, 'marked_for_deletion', False):
                    continue
                dx = boomer.transform.x - boid.transform.x
                dy = boomer.transform.y - boid.transform.y
                dist_sq = dx * dx + dy * dy
                contact_sum = boomer.collider.radius + boid.collider.radius
                if dist_sq < contact_sum * contact_sum:
                    contacted = True
                    break

            # Detonate on contact OR expired fuse; skip if neither condition is met
            if not contacted and not getattr(boomer, 'fuse_expired', False):
                continue

            # AoE sweep — mark every boid inside blast_radius
            boomer.has_detonated = True
            boomer.marked_for_deletion = True
            self._try_drop_soul(boomer.transform.x, boomer.transform.y)
            AssetLoader().play_sound("dwarf_explosion")
            if self.on_particle_spawned:
                self.on_particle_spawned("sapper_detonation", boomer.transform.x, boomer.transform.y)
            blast_radius_sq = boomer.blast_radius * boomer.blast_radius

            potential_blast_boids = spatial_hash.query_radius(boomer.transform.x, boomer.transform.y, boomer.blast_radius)
            for boid in potential_blast_boids:
                if getattr(boid, 'marked_for_deletion', False):
                    continue
                dx = boomer.transform.x - boid.transform.x
                dy = boomer.transform.y - boid.transform.y
                dist_sq = dx * dx + dy * dy
                if dist_sq < blast_radius_sq:
                    boid.marked_for_deletion = True
                    AssetLoader().play_sound("skeleton_pop")
                    if self.on_particle_spawned:
                        self.on_particle_spawned("skeleton_shatter", boid.transform.x, boid.transform.y)


        # --- LaserDrone Beam Hit Detection ---
        # Fires when behavior_system has set aiming_timer.is_firing = True.
        # Destroys every boid within the horizontal band at the drone's y position.
        # Punishes spread-out formations implicitly: scattered boids fan across many
        # y values and are more likely to intersect the beam band.
        drones = [e for e in entities
                  if getattr(e, 'enemy_type', None) == 'laser_drone'
                  and hasattr(e, 'aiming_timer')
                  and e.aiming_timer.is_firing]

        for drone in drones:
            for boid in boids:
                if getattr(boid, 'marked_for_deletion', False):
                    continue
                # Horizontal band check — pure subtraction, no sqrt
                vertical_dist = abs(boid.transform.y - drone.transform.y)
                if vertical_dist < drone.beam_width:
                    boid.marked_for_deletion = True
                    AssetLoader().play_sound("skeleton_pop")
                    if self.on_particle_spawned:
                        self.on_particle_spawned("skeleton_shatter", boid.transform.x, boid.transform.y)

