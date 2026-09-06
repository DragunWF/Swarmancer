import pygame
from utils.state import GameState

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
                    return "PLAY"
                elif self.controls_button.collidepoint(mouse_pos):
                    self.show_controls = True
                    return None
                elif self.settings_button.collidepoint(mouse_pos):
                    self.show_settings = True
                    return None
                    
            elif current_state == GameState.GAME_OVER:
                if self.restart_button.collidepoint(mouse_pos):
                    return "PLAY"
                elif self.menu_button.collidepoint(mouse_pos):
                    return "MAIN_MENU"

            elif current_state == GameState.VICTORY:
                if self.victory_menu_button.collidepoint(mouse_pos):
                    return "MAIN_MENU"
                    
        return None

    def draw_button(self, screen, rect, text):
        pygame.draw.rect(screen, (70, 70, 70), rect)
        pygame.draw.rect(screen, (200, 200, 200), rect, 2)
        text_surf = self.menu_font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    def draw_main_menu(self, screen, high_score):
        # Draw Title
        title_surf = self.title_font.render("SWARMANCER", True, (255, 50, 50))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title_surf, title_rect)
        
        # Draw High Score
        hs_surf = self.menu_font.render(f"High Score: {high_score:.1f}s", True, (255, 215, 0))
        hs_rect = hs_surf.get_rect(center=(self.screen_width // 2, 220))
        screen.blit(hs_surf, hs_rect)
        
        # Draw Buttons
        self.draw_button(screen, self.play_button, "Play")
        self.draw_button(screen, self.controls_button, "Controls")
        self.draw_button(screen, self.settings_button, "Settings")
        
        if self.show_controls:
            self._draw_overlay(screen, "Controls", ["Move: Mouse", "Dense State: Hold Left Click", "Scatter: Right Click (3s Cooldown)", "Pause: P Key"])
        elif self.show_settings:
            self._draw_overlay(screen, "Settings", ["Master Volume: [Placeholder]", "Music Volume: [Placeholder]"])

    def draw_game_over(self, screen, final_time, high_score):
        # Draw Game Over Text
        go_surf = self.title_font.render("GAME OVER", True, (255, 50, 50))
        go_rect = go_surf.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(go_surf, go_rect)
        
        # Draw Times
        time_surf = self.menu_font.render(f"Survived: {final_time:.1f}s", True, (255, 255, 255))
        time_rect = time_surf.get_rect(center=(self.screen_width // 2, 220))
        screen.blit(time_surf, time_rect)
        
        hs_surf = self.small_font.render(f"High Score: {high_score:.1f}s", True, (255, 215, 0))
        hs_rect = hs_surf.get_rect(center=(self.screen_width // 2, 260))
        screen.blit(hs_surf, hs_rect)
        
        # Draw Buttons
        self.draw_button(screen, self.restart_button, "Restart")
        self.draw_button(screen, self.menu_button, "Main Menu")

    def draw_victory(self, screen, final_time, souls):
        """Renders the Victory screen, displayed when the player survives all 10 minutes."""
        minutes = int(final_time) // 60
        seconds = int(final_time) % 60

        # Draw golden "VICTORY" title
        victory_surf = self.title_font.render("VICTORY", True, (255, 215, 0))
        victory_rect = victory_surf.get_rect(center=(self.screen_width // 2, 130))
        screen.blit(victory_surf, victory_rect)

        # Draw subtitle
        sub_surf = self.menu_font.render("You held the line for 10 minutes!", True, (200, 200, 200))
        sub_rect = sub_surf.get_rect(center=(self.screen_width // 2, 205))
        screen.blit(sub_surf, sub_rect)

        # Draw final survival time
        time_surf = self.menu_font.render(f"Survived: {minutes:02d}:{seconds:02d}", True, (255, 255, 255))
        time_rect = time_surf.get_rect(center=(self.screen_width // 2, 265))
        screen.blit(time_surf, time_rect)

        # Draw final soul count
        souls_surf = self.small_font.render(f"Souls Collected: {souls}", True, (255, 215, 0))
        souls_rect = souls_surf.get_rect(center=(self.screen_width // 2, 310))
        screen.blit(souls_surf, souls_rect)

        # Draw Main Menu button
        self.draw_button(screen, self.victory_menu_button, "Main Menu")

    def _draw_overlay(self, screen, title, lines):
        # Darken background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Draw Box
        box_width = 400
        box_height = 300
        box_rect = pygame.Rect(self.screen_width // 2 - box_width // 2, self.screen_height // 2 - box_height // 2, box_width, box_height)
        pygame.draw.rect(screen, (30, 30, 30), box_rect)
        pygame.draw.rect(screen, (200, 200, 200), box_rect, 2)
        
        title_surf = self.menu_font.render(title, True, (255, 255, 255))
        screen.blit(title_surf, (box_rect.x + 20, box_rect.y + 20))
        
        y_offset = 80
        for line in lines:
            line_surf = self.small_font.render(line, True, (200, 200, 200))
            screen.blit(line_surf, (box_rect.x + 20, box_rect.y + y_offset))
            y_offset += 30
            
        close_surf = self.small_font.render("Click anywhere to close", True, (150, 150, 150))
        screen.blit(close_surf, (box_rect.x + 20, box_rect.bottom - 40))
