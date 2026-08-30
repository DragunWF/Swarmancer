from pygame.math import Vector2

def safe_normalize(vector: Vector2) -> Vector2:
    """Returns a normalized vector safely without throwing division by zero."""
    if vector.length_squared() > 0:
        return vector.normalize()
    return Vector2(0, 0)
