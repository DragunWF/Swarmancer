import pygame
from utils.state import GameState

class ShopController:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 24)
        
        # Define buttons
        button_width, button_height = 200, 300
        padding = 40
        start_x = (screen_width - (3 * button_width + 2 * padding)) // 2
        y_pos = (screen_height - button_height) // 2
        
        self.buttons = [
            {"rect": pygame.Rect(start_x, y_pos, button_width, button_height), "id": 0, "color": (100, 100, 100), "hover_color": (150, 150, 150), "text": "Skeletal Archers\nCost: 10 Souls"},
            {"rect": pygame.Rect(start_x + button_width + padding, y_pos, button_width, button_height), "id": 1, "color": (100, 100, 100), "hover_color": (150, 150, 150), "text": "Upgrade B\nCost: 15 Souls"},
            {"rect": pygame.Rect(start_x + 2 * (button_width + padding), y_pos, button_width, button_height), "id": 2, "color": (100, 100, 100), "hover_color": (150, 150, 150), "text": "Upgrade C\nCost: 20 Souls"}
        ]
        
    def draw(self, screen: pygame.Surface, souls: int):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw souls count
        souls_text = self.font_large.render(f"Souls: {souls}", True, (255, 215, 0))
        screen.blit(souls_text, (self.screen_width // 2 - souls_text.get_width() // 2, 50))
        
        title_text = self.font_large.render("The Dark Altar", True, (200, 50, 50))
        screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 120))
        
        mouse_pos = pygame.mouse.get_pos()
        
        for btn in self.buttons:
            color = btn["hover_color"] if btn["rect"].collidepoint(mouse_pos) else btn["color"]
            pygame.draw.rect(screen, color, btn["rect"])
            pygame.draw.rect(screen, (255, 255, 255), btn["rect"], 3) # Border
            
            # Text rendering
            lines = btn["text"].split('\n')
            for i, line in enumerate(lines):
                text_surface = self.font_small.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (btn["rect"].centerx - text_surface.get_width() // 2, btn["rect"].y + 20 + i * 30))

    def handle_event(self, event: pygame.event.Event) -> int | None:
        """
        Handles events and returns the selected upgrade ID if clicked, else None.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for btn in self.buttons:
                if btn["rect"].collidepoint(mouse_pos):
                    return btn["id"]
        return None
