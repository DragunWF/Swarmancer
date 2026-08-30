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

        # 1-to-1 Attrition
        for enemy in enemies:
            if getattr(enemy, 'marked_for_deletion', False):
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
