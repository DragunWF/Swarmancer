import math

class CollisionSystem:
    def __init__(self, on_resource_collected=None):
        self.on_resource_collected = on_resource_collected

    def update(self, entities, dt):
        boids = [e for e in entities if hasattr(e, 'collider') and hasattr(e, 'physics') and not getattr(e, 'is_enemy', False)]
        resources = [e for e in entities if hasattr(e, 'collider') and hasattr(e, 'graphics') and hasattr(e, 'transform') and e.__class__.__name__ == 'Resource']
        enemies = [e for e in entities if getattr(e, 'is_enemy', False) and hasattr(e, 'collider')]

        for boid in boids:
            for resource in resources:
                if resource.marked_for_deletion:
                    continue

                dx = boid.transform.x - resource.transform.x
                dy = boid.transform.y - resource.transform.y
                distance_sq = dx * dx + dy * dy
                
                radius_sum = boid.collider.radius + resource.collider.radius
                if distance_sq < radius_sum * radius_sum:
                    resource.marked_for_deletion = True
                    if self.on_resource_collected:
                        self.on_resource_collected(resource.transform.x, resource.transform.y)

        # 1-to-1 Attrition (Grunts only — Boomers use is_trigger and are handled below)
        for enemy in enemies:
            if getattr(enemy, 'marked_for_deletion', False):
                continue
            # Skip trigger-type colliders; they are processed in the AoE block
            if getattr(enemy, 'collider', None) and enemy.collider.is_trigger:
                continue
            for boid in boids:
                if getattr(boid, 'marked_for_deletion', False):
                    continue
                dx = enemy.transform.x - boid.transform.x
                dy = enemy.transform.y - boid.transform.y
                distance_sq = dx * dx + dy * dy
                radius_sum = enemy.collider.radius + boid.collider.radius
                if distance_sq < radius_sum * radius_sum:
                    enemy.marked_for_deletion = True
                    boid.marked_for_deletion = True
                    break # One enemy pops exactly one boid

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
            for boid in boids:
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
            blast_radius_sq = boomer.blast_radius * boomer.blast_radius

            for boid in boids:
                if getattr(boid, 'marked_for_deletion', False):
                    continue
                dx = boomer.transform.x - boid.transform.x
                dy = boomer.transform.y - boid.transform.y
                dist_sq = dx * dx + dy * dy
                if dist_sq < blast_radius_sq:
                    boid.marked_for_deletion = True


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

