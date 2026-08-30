import asyncio
import pygame
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR
from entities.player import Player
from entities.boid import Boid
from systems.behavior_system import BehaviorSystem
from systems.movement_system import MovementSystem
from systems.render_system import RenderSystem

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
        
    # Initialize Systems
    behavior_system = BehaviorSystem()
    movement_system = MovementSystem()
    render_system = RenderSystem()
    
    systems = [behavior_system, movement_system, render_system]
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)

        # Systems update logic
        for system in systems:
            system.update(entities, dt)
        
        pygame.display.flip()
        
        # Required for pygbag / async web compatibility
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
