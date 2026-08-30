import asyncio
import pygame
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR
from entities.player import Player
from entities.boid import Boid
from entities.powerups import Resource
from systems.behavior_system import BehaviorSystem
from systems.movement_system import MovementSystem
from systems.render_system import RenderSystem
from systems.collision_system import CollisionSystem

async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Swarmancer")
    clock = pygame.time.Clock()
    
    # Initialize Entities
    entities = []
    player_x = SCREEN_WIDTH / 2
    player_y = SCREEN_HEIGHT / 2
    player = Player(player_x, player_y)
    entities.append(player)
    
    # Spawn 50 Boids around the initial player position
    for _ in range(50):
        boid = Boid(player_x + random.uniform(-60, 60), player_y + random.uniform(-60, 60))
        entities.append(boid)
        
    def on_resource_collected(x, y):
        # Spawn 3 new boids slightly offset from the grave
        for _ in range(3):
            entities.append(Boid(x + random.uniform(-20, 20), y + random.uniform(-20, 20)))

    # Initialize Systems
    behavior_system = BehaviorSystem()
    movement_system = MovementSystem()
    collision_system = CollisionSystem(on_resource_collected=on_resource_collected)
    render_system = RenderSystem()
    
    systems = [behavior_system, movement_system, collision_system, render_system]
    
    resource_timer = 0.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        resource_timer += dt
        
        if resource_timer > 3.0: # Spawn a grave every 3 seconds
            entities.append(Resource(random.uniform(50, SCREEN_WIDTH - 50), random.uniform(50, SCREEN_HEIGHT - 50)))
            resource_timer = 0.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)

        # Systems update logic
        for system in systems:
            system.update(entities, dt)
            
        # Cleanup deleted entities
        entities = [e for e in entities if not getattr(e, 'marked_for_deletion', False)]
        
        pygame.display.flip()
        
        # Required for pygbag / async web compatibility
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
