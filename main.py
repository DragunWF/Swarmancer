import asyncio
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR

async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Swarmancer")
    clock = pygame.time.Clock()
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)

        # Systems update logic will go here
        
        pygame.display.flip()
        
        # Required for pygbag / async web compatibility
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
