import pygame
from utils.asset_loader import AssetLoader
from ui.ui_utils import draw_slider

class PauseController:
    def __init__(self, screen_width, screen_height):
        pygame.font.init()
        self.title_font = pygame.font.SysFont(None, 72)
        self.menu_font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 24)
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        button_width = 250
        button_height = 50
        center_x = screen_width // 2 - button_width // 2
        
        self.continue_button = pygame.Rect(center_x, 200, button_width, button_height)
        self.menu_button = pygame.Rect(center_x, 270, button_width, button_height)
        
        # Audio Sliders (x, y, width, height)
        self.sfx_slider = pygame.Rect(center_x, 370, button_width, 20)
        self.music_slider = pygame.Rect(center_x, 440, button_width, 20)
        
        self.sfx_volume = 1.0
        self.music_volume = 1.0
        
        self.dragging_sfx = False
        self.dragging_music = False
        
        # Confirmation Dialog
        dialog_width = 400
        dialog_height = 200
        dialog_x = screen_width // 2 - dialog_width // 2
        dialog_y = screen_height // 2 - dialog_height // 2
        self.dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        
        btn_w = 100
        btn_h = 40
        self.yes_button = pygame.Rect(dialog_x + 80, dialog_y + 130, btn_w, btn_h)
        self.no_button = pygame.Rect(dialog_x + 220, dialog_y + 130, btn_w, btn_h)
        
        self.show_confirmation = False

    def handle_event(self, event):
        if self.show_confirmation:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.yes_button.collidepoint(event.pos):
                    AssetLoader().play_sound("ui_click")
                    self.show_confirmation = False
                    return "MAIN_MENU"
                elif self.no_button.collidepoint(event.pos):
                    AssetLoader().play_sound("ui_click")
                    self.show_confirmation = False
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.continue_button.collidepoint(event.pos):
                AssetLoader().play_sound("ui_click")
                return "RESUME"
            elif self.menu_button.collidepoint(event.pos):
                AssetLoader().play_sound("ui_click")
                self.show_confirmation = True
            elif self.sfx_slider.collidepoint(event.pos):
                self.dragging_sfx = True
                self._update_volume(event.pos[0], 'sfx')
            elif self.music_slider.collidepoint(event.pos):
                self.dragging_music = True
                self._update_volume(event.pos[0], 'music')
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_sfx = False
            self.dragging_music = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_sfx:
                self._update_volume(event.pos[0], 'sfx')
            elif self.dragging_music:
                self._update_volume(event.pos[0], 'music')
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                return "RESUME"
                
        return None

    def _update_volume(self, mouse_x, slider_type):
        slider = self.sfx_slider if slider_type == 'sfx' else self.music_slider
        # Calculate percentage (0.0 to 1.0)
        relative_x = mouse_x - slider.x
        percentage = max(0.0, min(1.0, relative_x / slider.width))
        
        if slider_type == 'sfx':
            self.sfx_volume = percentage
            AssetLoader().set_sfx_volume(self.sfx_volume)
        else:
            self.music_volume = percentage
            try:
                pygame.mixer.music.set_volume(self.music_volume)
            except pygame.error:
                pass # Mixer might not be initialized

    def draw_button(self, screen, rect, text):
        pygame.draw.rect(screen, (70, 70, 70), rect)
        pygame.draw.rect(screen, (200, 200, 200), rect, 2)
        text_surf = self.menu_font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    def draw(self, screen):
        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Title
        title_surf = self.title_font.render("PAUSED", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title_surf, title_rect)
        
        # Buttons
        self.draw_button(screen, self.continue_button, "Continue")
        self.draw_button(screen, self.menu_button, "Main Menu")
        
        # Sliders
        draw_slider(screen, self.sfx_slider, "SFX Volume", self.sfx_volume, self.small_font)
        draw_slider(screen, self.music_slider, "Music Volume", self.music_volume, self.small_font)
        
        # Confirmation Dialog
        if self.show_confirmation:
            pygame.draw.rect(screen, (30, 30, 30), self.dialog_rect)
            pygame.draw.rect(screen, (200, 50, 50), self.dialog_rect, 2)
            
            prompt_surf = self.menu_font.render("Are you sure?", True, (255, 255, 255))
            screen.blit(prompt_surf, prompt_surf.get_rect(center=(self.dialog_rect.centerx, self.dialog_rect.y + 40)))
            
            warn_surf = self.small_font.render("Progress will be lost.", True, (200, 150, 150))
            screen.blit(warn_surf, warn_surf.get_rect(center=(self.dialog_rect.centerx, self.dialog_rect.y + 80)))
            
            self.draw_button(screen, self.yes_button, "Yes")
            self.draw_button(screen, self.no_button, "No")
