import pygame
import math
from ui.ui_utils import draw_text_with_outline

class HUDController:
    def __init__(self, screen_width, screen_height):
        pygame.font.init()
        self.hud_font = pygame.font.SysFont(None, 36)
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Pre-render danger vignette
        self.vignette_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        for i in range(40):
            alpha = int(80 * (1 - (i / 40.0)))
            pygame.draw.rect(self.vignette_surface, (255, 0, 0, alpha), 
                             (i, i, screen_width - 2*i, screen_height - 2*i), 2)
                             
    def draw(self, screen, swarm_count, souls, current_survival_time, threat_level):
        # 1. Danger Vignette (Pulse if swarm < 15)
        if swarm_count < 15:
            pulse = (math.sin(current_survival_time * 6.0) + 1.0) / 2.0  # 0.0 to 1.0
            temp_vignette = self.vignette_surface.copy()
            # Modulate alpha based on pulse for a subtle warning
            temp_vignette.set_alpha(int(100 + pulse * 155))
            screen.blit(temp_vignette, (0, 0))

        # 2. Swarm Count (Top-Left)
        swarm_text = f"Swarm: {swarm_count}"
        swarm_size = self.hud_font.size(swarm_text)
        draw_text_with_outline(screen, swarm_text, self.hud_font, (232, 232, 232), (20 + swarm_size[0]//2, 20 + swarm_size[1]//2))
        
        # 3. Souls (Top-Right)
        souls_text = f"Souls: {souls}"
        souls_size = self.hud_font.size(souls_text)
        draw_text_with_outline(screen, souls_text, self.hud_font, (255, 215, 0), (self.screen_width - 20 - souls_size[0]//2, 20 + souls_size[1]//2))
        
        # 4. Survival Timer & Threat Level (Top-Center)
        minutes = int(current_survival_time) // 60
        seconds = int(current_survival_time) % 60
        timer_text = f"{minutes:02d}:{seconds:02d}  Threat Lv.{threat_level}"
        timer_size = self.hud_font.size(timer_text)
        draw_text_with_outline(screen, timer_text, self.hud_font, (232, 232, 232), (self.screen_width // 2, 20 + timer_size[1]//2))
