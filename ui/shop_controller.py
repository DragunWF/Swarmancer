import pygame
import random
from utils.state import GameState

class ShopController:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 24)
        
        # Define buttons
        self.button_width, self.button_height = 200, 300
        self.padding = 40
        self.start_x = (screen_width - (3 * self.button_width + 2 * self.padding)) // 2
        self.y_pos = (screen_height - self.button_height) // 2
        
        self.all_upgrades = [
            {"id": 0, "name": "Skeletal Archers", "cost": 10},
            {"id": 1, "name": "Grave Robber's Yield", "cost": 15},
            {"id": 2, "name": "Evasion Mastery", "cost": 15},
            {"id": 3, "name": "Bone Shrapnel", "cost": 20},
            {"id": 4, "name": "Necrotic Momentum", "cost": 20}
        ]
        self.buttons = []
        self.refresh_upgrades()
        
    def refresh_upgrades(self):
        selected = random.sample(self.all_upgrades, 3)
        self.buttons = []
        for i, upg in enumerate(selected):
            rect = pygame.Rect(self.start_x + i * (self.button_width + self.padding), self.y_pos, self.button_width, self.button_height)
            self.buttons.append({
                "rect": rect,
                "id": upg["id"],
                "color": (100, 100, 100),
                "hover_color": (150, 150, 150),
                "text": f"{upg['name']}\nCost: {upg['cost']} Souls",
                "cost": upg["cost"]
            })
        
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
