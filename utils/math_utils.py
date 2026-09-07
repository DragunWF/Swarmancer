from pygame.math import Vector2
import math

def safe_normalize(vector: Vector2) -> Vector2:
    """Returns a normalized vector safely without throwing division by zero."""
    if vector.length_squared() > 0:
        return vector.normalize()
    return Vector2(0, 0)

def velocity_to_direction(vx: float, vy: float) -> str:
    """Maps a 2D velocity to one of 8 cardinal/ordinal directions."""
    if abs(vx) < 0.1 and abs(vy) < 0.1:
        return "south"
    
    # Pygame's Y axis goes down, so we negate vy for standard trig angles
    angle = math.degrees(math.atan2(-vy, vx))
    if angle < 0:
        angle += 360
        
    if 22.5 <= angle < 67.5:
        return "north-east"
    elif 67.5 <= angle < 112.5:
        return "north"
    elif 112.5 <= angle < 157.5:
        return "north-west"
    elif 157.5 <= angle < 202.5:
        return "west"
    elif 202.5 <= angle < 247.5:
        return "south-west"
    elif 247.5 <= angle < 292.5:
        return "south"
    elif 292.5 <= angle < 337.5:
        return "south-east"
    else:
        return "east"
