from systems.system import System
from pygame.math import Vector2
import pygame
import random
import math

class BehaviorSystem(System):
    def __init__(self):
        self.cursor_weight = 2.0
        self.separation_weight = 2.2
        self.cohesion_weight = 0.8
        self.alignment_weight = 0.8
        
        self.perception_radius = 55.0
        self.separation_radius = 22.0
        self.arrival_radius = 65.0
        self.max_force = 1200.0

    def update(self, entities, dt):
        player = None
        boids = []
        enemies = []
        
        for entity in entities:
            if hasattr(entity, 'is_player'):
                player = entity
            elif hasattr(entity, 'physics') and hasattr(entity, 'transform'):
                if getattr(entity, 'is_enemy', False):
                    enemies.append(entity)
                else:
                    boids.append(entity)

        if not player:
            return

        # Handle ScatterTimer countdown & active burst duration
        is_scattering = False
        just_triggered_scatter = False

        if hasattr(player, 'scatter_timer'):
            st = player.scatter_timer
            if st.current_time > 0.0:
                st.current_time -= dt
                if st.current_time < 0.0:
                    st.current_time = 0.0
                    
            if st.active_time > 0.0:
                st.active_time -= dt
                if st.active_time < 0.0:
                    st.active_time = 0.0
                is_scattering = True

        # Update player position to mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if pygame.mouse.get_focused() or (mouse_x != 0 or mouse_y != 0):
            player.transform.x = mouse_x
            player.transform.y = mouse_y
            
        mouse_buttons = pygame.mouse.get_pressed()
        if hasattr(player, 'state'):
            player.state.is_dense = mouse_buttons[0]
            
        if mouse_buttons[2] and hasattr(player, 'scatter_timer'):  # Right click
            st = player.scatter_timer
            if st.current_time <= 0.0:
                st.current_time = st.cooldown_duration
                st.active_time = st.scatter_duration
                is_scattering = True
                just_triggered_scatter = True
        
        target_pos = Vector2(player.transform.x, player.transform.y)

        for boid in boids:
            boid_pos = Vector2(boid.transform.x, boid.transform.y)

            # Instant velocity explosion when scatter is triggered
            if just_triggered_scatter:
                away_vec = boid_pos - target_pos
                if away_vec.length_squared() > 0:
                    away_dir = away_vec.normalize()
                else:
                    angle = random.uniform(0, 2 * math.pi)
                    away_dir = Vector2(math.cos(angle), math.sin(angle))
                boid.physics.velocity = away_dir * 650.0

            max_speed = 750.0 if is_scattering else boid.physics.max_speed
            
            if is_scattering:
                # Continuous outward steering during scatter burst
                away_vec = boid_pos - target_pos
                if away_vec.length_squared() > 0:
                    desired = away_vec.normalize() * max_speed
                else:
                    desired = Vector2(max_speed, 0)
                scatter_steer = desired - boid.physics.velocity
                total_steer = scatter_steer * 4.0
                max_allowed_force = 4000.0
            else:
                # 1. Cursor Attraction (Seek with Arrival)
                to_target = target_pos - boid_pos
                dist_to_target = to_target.length()
                if dist_to_target > 0:
                    if dist_to_target < self.arrival_radius:
                        desired_speed = max_speed * (dist_to_target / self.arrival_radius)
                    else:
                        desired_speed = max_speed
                    desired = to_target.normalize() * desired_speed
                    cursor_steer = desired - boid.physics.velocity
                    if cursor_steer.length_squared() > self.max_force ** 2:
                        cursor_steer.scale_to_length(self.max_force)
                else:
                    cursor_steer = Vector2(0, 0)

                # 2. Local Flocking (Separation, Cohesion, Alignment)
                center_of_mass = Vector2(0, 0)
                avg_velocity = Vector2(0, 0)
                separation_repulsion = Vector2(0, 0)
                neighbors = 0
                
                for other in boids:
                    if boid is other:
                        continue
                    other_pos = Vector2(other.transform.x, other.transform.y)
                    dist = boid_pos.distance_to(other_pos)
                    
                    if dist < self.perception_radius:
                        center_of_mass += other_pos
                        avg_velocity += other.physics.velocity
                        neighbors += 1
                        
                        if 0 < dist < self.separation_radius:
                            diff = (boid_pos - other_pos).normalize() / dist
                            separation_repulsion += diff

                cohesion_steer = Vector2(0, 0)
                alignment_steer = Vector2(0, 0)
                separation_steer = Vector2(0, 0)

                if neighbors > 0:
                    # Cohesion
                    center_of_mass /= neighbors
                    to_com = center_of_mass - boid_pos
                    if to_com.length_squared() > 0:
                        desired = to_com.normalize() * max_speed
                        cohesion_steer = desired - boid.physics.velocity
                        if cohesion_steer.length_squared() > self.max_force ** 2:
                            cohesion_steer.scale_to_length(self.max_force)

                    # Alignment
                    avg_velocity /= neighbors
                    if avg_velocity.length_squared() > 0:
                        desired = avg_velocity.normalize() * max_speed
                        alignment_steer = desired - boid.physics.velocity
                        if alignment_steer.length_squared() > self.max_force ** 2:
                            alignment_steer.scale_to_length(self.max_force)

                # Separation
                if separation_repulsion.length_squared() > 0:
                    desired = separation_repulsion.normalize() * max_speed
                    separation_steer = desired - boid.physics.velocity
                    if separation_steer.length_squared() > self.max_force ** 2:
                        separation_steer.scale_to_length(self.max_force)

                # Combine forces
                is_dense = hasattr(player, 'state') and player.state.is_dense
                active_cursor_weight = self.cursor_weight * (3.0 if is_dense else 1.0)
                active_cohesion_weight = self.cohesion_weight * (5.0 if is_dense else 1.0)
                active_separation_weight = self.separation_weight * (0.5 if is_dense else 1.0)
                
                total_steer = (
                    cursor_steer * active_cursor_weight +
                    separation_steer * active_separation_weight +
                    cohesion_steer * active_cohesion_weight +
                    alignment_steer * self.alignment_weight
                )
                max_allowed_force = self.max_force

            # Cap total steering acceleration
            if total_steer.length_squared() > max_allowed_force ** 2:
                total_steer.scale_to_length(max_allowed_force)

            boid.physics.acceleration += total_steer / boid.physics.mass

        # Enemy Tracking Logic
        for enemy in enemies:
            enemy_pos = Vector2(enemy.transform.x, enemy.transform.y)
            to_target = target_pos - enemy_pos
            if to_target.length_squared() > 0:
                desired = to_target.normalize() * enemy.physics.max_speed
                steer = desired - enemy.physics.velocity
                if steer.length_squared() > self.max_force ** 2:
                    steer.scale_to_length(self.max_force)
                enemy.physics.acceleration += steer / enemy.physics.mass

        # --- Boomer Fuse Tick ---
        # The fuse only ticks while the Boomer is within fuse_proximity_radius of the player
        # cursor. This prevents far-away Boomers from detonating before they've had a chance
        # to reach the swarm. The elapsed value pauses (but does not reset) if the Boomer
        # moves out of range, so repeated approach/retreat cannot stall the fuse indefinitely.
        # Sole responsibility: advance timer data and set fuse_expired. No AoE math here.
        for entity in entities:
            if getattr(entity, 'enemy_type', None) != 'boomer':
                continue
            if getattr(entity, 'has_detonated', False) or getattr(entity, 'marked_for_deletion', False):
                continue
            if not hasattr(entity, 'fuse_timer'):
                continue

            # Proximity gate — squared distance to player cursor (no sqrt)
            dx = entity.transform.x - target_pos.x
            dy = entity.transform.y - target_pos.y
            dist_sq = dx * dx + dy * dy
            prox_sq = entity.fuse_proximity_radius * entity.fuse_proximity_radius

            if dist_sq > prox_sq:
                continue  # Still too far away — fuse stays paused

            entity.fuse_timer.elapsed += dt
            if entity.fuse_timer.elapsed >= entity.fuse_timer.duration:
                entity.fuse_expired = True

        # --- LaserDrone AimingTimer Tick ---
        # Advances each drone through its telegraph → fire → reset cycle.
        # Sole responsibility: update timer data. Hit detection is in collision_system.
        for entity in entities:
            if getattr(entity, 'enemy_type', None) != 'laser_drone':
                continue
            if not hasattr(entity, 'aiming_timer'):
                continue

            at = entity.aiming_timer

            if not at.is_firing:
                # Telegraph phase: accumulate charge time
                at.elapsed += dt
                if at.elapsed >= at.charge_duration:
                    # Threshold reached — begin firing
                    at.is_firing = True
                    at.elapsed = 0.0
            else:
                # Active firing phase: count down beam duration
                at.fire_elapsed += dt
                if at.fire_elapsed >= at.fire_duration:
                    # Firing complete — reset full cycle back to telegraph
                    at.is_firing = False
                    at.fire_elapsed = 0.0
                    at.elapsed = 0.0

        # --- LifespanTimer Tick ---
        # Marks entities for deletion once their lifespan expires
        for entity in entities:
            if not hasattr(entity, 'lifespan_timer'):
                continue
            if getattr(entity, 'marked_for_deletion', False):
                continue
                
            entity.lifespan_timer.elapsed += dt
            if entity.lifespan_timer.elapsed >= entity.lifespan_timer.duration:
                entity.marked_for_deletion = True
