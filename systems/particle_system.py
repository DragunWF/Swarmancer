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

            # Particle Kinetics Logic
            if hasattr(entity, 'kinetics') and hasattr(entity, 'transform'):
                kin = entity.kinetics
                # Apply decay (friction)
                # drag is heavily applied, e.g., drag ** dt
                decay = kin.drag ** dt
                kin.vx *= decay
                kin.vy *= decay
                
                # Apply velocity
                entity.transform.x += kin.vx * dt
                entity.transform.y += kin.vy * dt
