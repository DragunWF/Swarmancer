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
                             
        # Pre-render pause hint
        self.pause_font = pygame.font.SysFont(None, 24)
        self.pause_text_surf = self.pause_font.render("Press [P] to Pause", True, (232, 232, 232))
        self.pause_text_shadow = self.pause_font.render("Press [P] to Pause", True, (0, 0, 0))
                             
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
        
        # 5. Action Bar
        if player and hasattr(player, 'scatter_timer'):
            self._draw_action_bar(screen, player, current_survival_time)

    def _draw_action_bar(self, screen, player, current_survival_time):
        bar_width = 200
        bar_height = 15
        x_center = self.screen_width // 2
        y_center = self.screen_height - bar_height - 20
        
        scatter_progress = 1.0
        if hasattr(player, 'scatter_timer'):
            st = player.scatter_timer
            if st.cooldown_duration > 0:
                scatter_progress = 1.0 - (st.current_time / st.cooldown_duration)
                
        dense_progress = 1.0
        if hasattr(player, 'dense_timer'):
            dt_timer = player.dense_timer
            if dt_timer.cooldown_time > 0.0:
                dense_progress = 1.0 - (dt_timer.cooldown_time / dt_timer.cooldown_duration)
            elif dt_timer.active_time > 0.0:
                dense_progress = 1.0 - (dt_timer.active_time / dt_timer.max_duration)
                
        progress = min(scatter_progress, dense_progress)
        progress = max(0.0, min(1.0, progress))
        
        # 1. Base Dark Bar with border
        border_rect = pygame.Rect(x_center - bar_width // 2, y_center, bar_width, bar_height)
        
        # We need a surface for the background to support alpha if we want
        bg_surf = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        bg_surf.fill((26, 26, 26, 200))
        screen.blit(bg_surf, border_rect.topleft)
        pygame.draw.rect(screen, (200, 200, 200), border_rect, 2)
        
        # 2. Horizontal Fill (Necrotic Cyan)
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(x_center - bar_width // 2, y_center, fill_width, bar_height)
            pygame.draw.rect(screen, (0, 255, 255), fill_rect)
            
        # 3. Pulse / Glow when ready
        if progress >= 1.0:
            pulse_margin = int(4 * math.sin(current_survival_time * 5.0) + 4)
            if pulse_margin > 0:
                glow_rect = pygame.Rect(x_center - bar_width // 2 - pulse_margin, y_center - pulse_margin, bar_width + pulse_margin * 2, bar_height + pulse_margin * 2)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (0, 255, 255, 50), glow_surf.get_rect(), border_radius=4)
                screen.blit(glow_surf, glow_rect.topleft)
            
        # 4. Text Hints above the bar
        text_color = (232, 232, 232) if progress >= 1.0 else (100, 100, 100)
        draw_text_with_outline(screen, "[LMB] Condense  |  Scatter [RMB]", self.hud_font, text_color, (x_center, y_center - 20))
        
        # 5. Pause Hint (above the ability text)
        pause_x = x_center - self.pause_text_surf.get_width() // 2
        pause_y = y_center - 55 - self.pause_text_surf.get_height() // 2
        
        screen.blit(self.pause_text_shadow, (pause_x + 2, pause_y + 2))
        screen.blit(self.pause_text_surf, (pause_x, pause_y))
