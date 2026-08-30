import math

class CollisionSystem:
    def __init__(self, on_resource_collected=None):
        self.on_resource_collected = on_resource_collected

    def update(self, entities, dt):
        boids = [e for e in entities if hasattr(e, 'collider') and hasattr(e, 'physics')]
        resources = [e for e in entities if hasattr(e, 'collider') and hasattr(e, 'graphics') and hasattr(e, 'transform') and e.__class__.__name__ == 'Resource']

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
