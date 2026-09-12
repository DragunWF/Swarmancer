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
                             
    def draw(self, screen, player, swarm_count, current_survival_time, threat_level):
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
        souls = player.souls if player else 0
        souls_text = f"Souls: {souls}"
        souls_size = self.hud_font.size(souls_text)
        draw_text_with_outline(screen, souls_text, self.hud_font, (255, 215, 0), (self.screen_width - 20 - souls_size[0]//2, 20 + souls_size[1]//2))
        
        # 4. Survival Timer & Threat Level (Top-Center)
        minutes = int(current_survival_time) // 60
        seconds = int(current_survival_time) % 60
        timer_text = f"{minutes:02d}:{seconds:02d}  Threat Lv.{threat_level}"
        timer_size = self.hud_font.size(timer_text)
        draw_text_with_outline(screen, timer_text, self.hud_font, (232, 232, 232), (self.screen_width // 2, 20 + timer_size[1]//2))
        
        # 5. Command Orb
        if player and hasattr(player, 'scatter_timer'):
            self._draw_command_orb(screen, player, current_survival_time)

    def _draw_command_orb(self, screen, player, current_survival_time):
        radius = 30
        x_center = self.screen_width // 2
        y_center = self.screen_height - radius - 20
        
        st = player.scatter_timer
        progress = 1.0 - (st.current_time / st.cooldown_duration) if st.cooldown_duration > 0 else 1.0
        progress = max(0.0, min(1.0, progress))
        
        # 1. Base Dark Orb
        base_orb = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(base_orb, (20, 20, 20, 200), (radius, radius), radius)
        screen.blit(base_orb, (x_center - radius, y_center - radius))
        
        # 2. Liquid Fill (Necrotic Cyan)
        if progress > 0.0:
            fill_orb = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(fill_orb, (0, 255, 255, 255), (radius, radius), radius)
            
            fill_h = int(radius * 2 * progress)
            if fill_h > 0:
                fill_rect = pygame.Rect(0, radius * 2 - fill_h, radius * 2, fill_h)
                cropped_fill = fill_orb.subsurface(fill_rect)
                screen.blit(cropped_fill, (x_center - radius, y_center - radius + (radius * 2 - fill_h)))
                
        # 3. Pulse / Glow when ready
        if progress >= 1.0:
            pulse_radius = radius + int(5 * math.sin(current_survival_time * 5.0))
            glow_surf = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (0, 255, 255, 50), (pulse_radius, pulse_radius), pulse_radius)
            screen.blit(glow_surf, (x_center - pulse_radius, y_center - pulse_radius))
            
        # 4. Flanking Text
        draw_text_with_outline(screen, "[LMB] Condense", self.hud_font, (232, 232, 232), (x_center - radius - 90, y_center))
        draw_text_with_outline(screen, "Scatter [RMB]", self.hud_font, (232, 232, 232), (x_center + radius + 90, y_center))
