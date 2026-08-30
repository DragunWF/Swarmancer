from systems.system import System
import pygame

class RenderSystem(System):
    def update(self, entities, dt):
        screen = pygame.display.get_surface()
        if not screen:
            return
            
        for entity in entities:
            if hasattr(entity, 'graphics') and hasattr(entity, 'transform'):
                gfx = entity.graphics
                pos = (int(entity.transform.x), int(entity.transform.y))
                pygame.draw.circle(screen, gfx.color, pos, int(gfx.scale))
                
            elif hasattr(entity, 'is_player'):
                pos = (int(entity.transform.x), int(entity.transform.y))
                pygame.draw.circle(screen, (255, 0, 0), pos, 5, 1)
