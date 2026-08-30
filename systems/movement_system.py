from systems.system import System

class MovementSystem(System):
    def update(self, entities, dt):
        for entity in entities:
            if hasattr(entity, 'physics') and hasattr(entity, 'transform'):
                physics = entity.physics
                transform = entity.transform
                
                physics.velocity += physics.acceleration * dt
                
                if physics.velocity.length_squared() > physics.max_speed ** 2:
                    physics.velocity.scale_to_length(physics.max_speed)
                    
                transform.x += physics.velocity.x * dt
                transform.y += physics.velocity.y * dt
                
                physics.acceleration.update(0, 0)
