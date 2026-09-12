import math

class ParticleSystem:
    def update(self, entities, dt):
        for entity in entities:
            # Check if entity has both LifespanTimer and Graphics
            if hasattr(entity, 'lifespan_timer') and hasattr(entity, 'graphics'):
                timer = entity.lifespan_timer
                timer.elapsed += dt
                
                # Calculate remaining life ratio
                life_ratio = 1.0 - (timer.elapsed / timer.duration)
                
                if life_ratio <= 0.0:
                    entity.marked_for_deletion = True
                else:
                    # Update graphics alpha to fade out
                    # Alpha should go from 255 to 0 as life_ratio goes from 1.0 to 0.0
                    entity.graphics.alpha = max(0, int(255 * life_ratio))

            # Particle Tracking Logic
            if hasattr(entity, 'target_tracker') and hasattr(entity, 'transform'):
                tracker = entity.target_tracker
                if tracker.target and not getattr(tracker.target, 'marked_for_deletion', False):
                    dx = tracker.target.transform.x - entity.transform.x
                    dy = tracker.target.transform.y - entity.transform.y
                    
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        nx = dx / dist
                        ny = dy / dist
                        
                        life_ratio = 1.0
                        if hasattr(entity, 'lifespan_timer'):
                            timer = entity.lifespan_timer
                            life_ratio = max(0.0, 1.0 - (timer.elapsed / timer.duration))
                        
                        tangent_weight = life_ratio * tracker.spiral_factor
                        direct_weight = tracker.speed
                        
                        vx = (nx * direct_weight) + (-ny * tangent_weight)
                        vy = (ny * direct_weight) + (nx * tangent_weight)
                        
                        entity.transform.x += vx * dt
                        entity.transform.y += vy * dt
                else:
                    # Target is dead, force delete next frame
                    if hasattr(entity, 'lifespan_timer'):
                         entity.lifespan_timer.elapsed = entity.lifespan_timer.duration
