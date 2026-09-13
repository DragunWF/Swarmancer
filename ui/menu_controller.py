import pygame
from utils.state import GameState
from utils.asset_loader import AssetLoader
from ui.ui_utils import draw_text_with_outline, draw_polished_button

# Y-position of the victory "Main Menu" button — used by both draw and handle_event
_VICTORY_MENU_BTN_Y = 380

class MenuController:
    def __init__(self, screen_width, screen_height):
        pygame.font.init()
        self.title_font = pygame.font.SysFont(None, 72)
        self.menu_font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 24)
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        button_width = 200
        button_height = 50
        center_x = screen_width // 2 - button_width // 2
        
        self.play_button = pygame.Rect(center_x, 300, button_width, button_height)
        self.controls_button = pygame.Rect(center_x, 370, button_width, button_height)
        self.settings_button = pygame.Rect(center_x, 440, button_width, button_height)
        
        self.restart_button = pygame.Rect(center_x, 350, button_width, button_height)
        self.menu_button = pygame.Rect(center_x, 420, button_width, button_height)
        self.victory_menu_button = pygame.Rect(center_x, _VICTORY_MENU_BTN_Y, button_width, button_height)
        
        self.show_controls = False
        self.show_settings = False
        
        # Audio volumes (placeholder logic for Settings)
        self.master_volume = 1.0
        self.music_volume = 1.0

    def handle_event(self, event, current_state):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            if self.show_controls or self.show_settings:
                # Any click closes the overlays for now
                self.show_controls = False
                self.show_settings = False
                return None
                
            if current_state == GameState.MENU:
                if self.play_button.collidepoint(mouse_pos):
                    AssetLoader().play_sound("ui_click")
                    return "PLAY"
                elif self.controls_button.collidepoint(mouse_pos):
                    AssetLoader().play_sound("ui_click")
                    self.show_controls = True
                    return None
                elif self.settings_button.collidepoint(mouse_pos):
                    AssetLoader().play_sound("ui_click")
                    self.show_settings = True
                    return None
                    
            elif current_state == GameState.GAME_OVER:
                if self.restart_button.collidepoint(mouse_pos):
                    AssetLoader().play_sound("ui_click")
                    return "PLAY"
                elif self.menu_button.collidepoint(mouse_pos):
                    AssetLoader().play_sound("ui_click")
                    return "MAIN_MENU"

            elif current_state == GameState.VICTORY:
                if self.victory_menu_button.collidepoint(mouse_pos):
                    AssetLoader().play_sound("ui_click")
                    return "MAIN_MENU"
                    
        return None

    def _draw_dimming_overlay(self, screen):
        dim_overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        dim_overlay.fill((0, 0, 0, 150))
        screen.blit(dim_overlay, (0, 0))

    def draw_main_menu(self, screen, high_score):
        bg = AssetLoader().get_menu_background()
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((20, 20, 20))
            
        self._draw_dimming_overlay(screen)
            
        # Draw Title
        draw_text_with_outline(screen, "SWARMANCER", self.title_font, (232, 232, 232), (self.screen_width // 2, 150))
        
        # Draw High Score
        draw_text_with_outline(screen, f"High Score: {high_score:.1f}s", self.menu_font, (255, 215, 0), (self.screen_width // 2, 220))
        
        # Draw Buttons
        draw_polished_button(screen, self.play_button, "Play", self.menu_font)
        draw_polished_button(screen, self.controls_button, "Controls", self.menu_font)
        draw_polished_button(screen, self.settings_button, "Settings", self.menu_font)
        
        if self.show_controls:
            self._draw_overlay(screen, "Controls", ["Move: Mouse", "Dense State: Hold Left Click", "Scatter: Right Click (3s Cooldown)", "Pause: P Key"])
        elif self.show_settings:
            self._draw_overlay(screen, "Settings", ["Master Volume: [Placeholder]", "Music Volume: [Placeholder]"])

    def draw_game_over(self, screen, final_time, high_score):
        self._draw_dimming_overlay(screen)
        
        # Draw Game Over Text
        draw_text_with_outline(screen, "GAME OVER", self.title_font, (255, 50, 50), (self.screen_width // 2, 150))
        
        # Draw Times
        draw_text_with_outline(screen, f"Survived: {final_time:.1f}s", self.menu_font, (232, 232, 232), (self.screen_width // 2, 220))
        
        draw_text_with_outline(screen, f"High Score: {high_score:.1f}s", self.small_font, (255, 215, 0), (self.screen_width // 2, 260))
        
        # Draw Buttons
        draw_polished_button(screen, self.restart_button, "Restart", self.menu_font)
        draw_polished_button(screen, self.menu_button, "Main Menu", self.menu_font)

    def draw_victory(self, screen, final_time, souls):
        """Renders the Victory screen, displayed when the player survives all 10 minutes."""
        self._draw_dimming_overlay(screen)
        
        minutes = int(final_time) // 60
        seconds = int(final_time) % 60

        # Draw golden "VICTORY" title
        draw_text_with_outline(screen, "VICTORY", self.title_font, (255, 215, 0), (self.screen_width // 2, 130))

        # Draw subtitle
        draw_text_with_outline(screen, "You held the line for 10 minutes!", self.menu_font, (232, 232, 232), (self.screen_width // 2, 205))

        # Draw final survival time
        draw_text_with_outline(screen, f"Survived: {minutes:02d}:{seconds:02d}", self.menu_font, (232, 232, 232), (self.screen_width // 2, 265))

        # Draw final soul count
        draw_text_with_outline(screen, f"Souls Collected: {souls}", self.small_font, (255, 215, 0), (self.screen_width // 2, 310))

        # Draw Main Menu button
        draw_polished_button(screen, self.victory_menu_button, "Main Menu", self.menu_font)

    def _draw_overlay(self, screen, title, lines):
        # Darken background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Draw Box
        box_width = 400
        box_height = 300
        box_rect = pygame.Rect(self.screen_width // 2 - box_width // 2, self.screen_height // 2 - box_height // 2, box_width, box_height)
        pygame.draw.rect(screen, (26, 26, 26), box_rect)
        pygame.draw.rect(screen, (232, 232, 232), box_rect, 2)
        
        title_center = (box_rect.x + 20 + self.menu_font.size(title)[0] // 2, box_rect.y + 20 + self.menu_font.size(title)[1] // 2)
        draw_text_with_outline(screen, title, self.menu_font, (255, 215, 0), title_center)
        
        y_offset = 80
        for line in lines:
            line_size = self.small_font.size(line)
            line_center = (box_rect.x + 20 + line_size[0] // 2, box_rect.y + y_offset + line_size[1] // 2)
            draw_text_with_outline(screen, line, self.small_font, (232, 232, 232), line_center)
            y_offset += 30
            
        close_text = "Click anywhere to close"
        close_size = self.small_font.size(close_text)
        close_center = (box_rect.x + 20 + close_size[0] // 2, box_rect.bottom - 40 + close_size[1] // 2)
        draw_text_with_outline(screen, close_text, self.small_font, (150, 150, 150), close_center)
