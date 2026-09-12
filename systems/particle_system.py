import math
import random
from entities.particles import Particle

class ParticleEmitter:
    @staticmethod
    def emit(effect_type: str, x: float, y: float) -> list:
        particles = []
        if effect_type == "skeleton_shatter":
            # 8-10 bone-white, 2-4 necrotic cyan
            for _ in range(random.randint(8, 10)):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(80, 180)
                vx, vy = math.cos(angle) * speed, math.sin(angle) * speed
                particles.append(Particle(x, y, vx, vy, color=(245, 245, 220), drag=0.05, duration=random.uniform(0.4, 0.7), scale=random.uniform(2.0, 4.0)))
            for _ in range(random.randint(2, 4)):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(80, 180)
                vx, vy = math.cos(angle) * speed, math.sin(angle) * speed
                particles.append(Particle(x, y, vx, vy, color=(0, 255, 255), drag=0.05, duration=random.uniform(0.4, 0.7), scale=random.uniform(3.0, 5.0)))
                
        elif effect_type == "vanguard_pop":
            # chaotic burst of sunbaked tan and sweat-stained yellow
            for _ in range(random.randint(12, 16)):
                color = random.choice([(210, 180, 140), (255, 219, 88)])
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(100, 220)
                vx, vy = math.cos(angle) * speed, math.sin(angle) * speed
                particles.append(Particle(x, y, vx, vy, color=color, drag=0.05, duration=random.uniform(0.3, 0.6)))

        elif effect_type == "sun_wizard_teleport":
            # high-velocity solar-gold and bright white, non-fading
            for _ in range(random.randint(30, 45)):
                color = random.choice([(255, 215, 0), (255, 255, 255)])
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(250, 500)
                vx, vy = math.cos(angle) * speed, math.sin(angle) * speed
                particles.append(Particle(x, y, vx, vy, color=color, drag=0.01, duration=random.uniform(0.4, 0.7), fade=False))

        elif effect_type == "sun_wizard_death":
            # high-velocity exit teleportation burst, non-fading
            for _ in range(random.randint(30, 45)):
                color = random.choice([(255, 215, 0), (255, 255, 255)])
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(250, 500)
                vx, vy = math.cos(angle) * speed, math.sin(angle) * speed
                particles.append(Particle(x, y, vx, vy, color=color, drag=0.01, duration=random.uniform(0.4, 0.7), fade=False))

        elif effect_type == "sapper_detonation":
            # dense radial blast of deep copper, charred brown, and blazing solar-gold sparks with heavy drag
            for _ in range(random.randint(40, 60)):
                color = random.choice([(184, 115, 51), (92, 64, 51), (255, 215, 0)])
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(250, 450)
                vx, vy = math.cos(angle) * speed, math.sin(angle) * speed
                particles.append(Particle(x, y, vx, vy, color=color, drag=0.80, duration=random.uniform(0.6, 1.2), scale=random.uniform(4.0, 7.0)))

        return particles


class ParticleSystem:
    def __init__(self, on_particle_spawned=None):
        self.on_particle_spawned = on_particle_spawned

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
                    if getattr(entity, 'enemy_type', None) == 'laser_drone':
                        if self.on_particle_spawned:
                            self.on_particle_spawned("sun_wizard_death", entity.transform.x, entity.transform.y)
                elif getattr(entity, 'is_particle', False) and getattr(entity, 'fade', True):
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
