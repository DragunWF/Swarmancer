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
            {"id": 0, "name": "Skeletal Archers", "desc": "Mutate ranged units to shoot down the charging peasant militia.", "cost": 10},
            {"id": 1, "name": "Grave Robber's Yield", "desc": "Multiply the amount of skeleton minions resurrected at each glowing grave.", "cost": 15},
            {"id": 2, "name": "Evasion Mastery", "desc": "Lower scatter cooldown to rapidly escape a stationary stone wizard tower and its holy light laser beam.", "cost": 15},
            {"id": 3, "name": "Bone Shrapnel", "desc": "Minions shatter upon death, dealing splash damage to the charging peasant militia.", "cost": 20},
            {"id": 4, "name": "Necrotic Momentum", "desc": "Increase top speed to quickly condense and evade bombs from a heavy dwarf sapper.", "cost": 20}
        ]
        self.available_upgrades = self.all_upgrades.copy()
        self.buttons = []
        self.continue_btn_rect = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 + 50, 200, 60)
        self.refresh_upgrades()
        
    def refresh_upgrades(self):
        self.buttons = []
        if not self.available_upgrades:
            return
            
        num_selections = min(3, len(self.available_upgrades))
        selected = random.sample(self.available_upgrades, num_selections)
        
        # Recalculate start_x based on how many buttons we actually have
        current_start_x = (self.screen_width - (num_selections * self.button_width + (num_selections - 1) * self.padding)) // 2
        
        for i, upg in enumerate(selected):
            rect = pygame.Rect(current_start_x + i * (self.button_width + self.padding), self.y_pos, self.button_width, self.button_height)
            self.buttons.append({
                "rect": rect,
                "id": upg["id"],
                "color": (100, 100, 100),
                "hover_color": (150, 150, 150),
                "text": f"{upg['name']}\n\nCost: {upg['cost']} Souls\n\n{upg['desc']}",
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
        
        mouse_pos = pygame.mouse.get_pos()
        
        if not self.available_upgrades:
            title_text = self.font_large.render("The Dark Altar is Dormant", True, (150, 150, 150))
            screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 120))
            
            color = (150, 150, 150) if self.continue_btn_rect.collidepoint(mouse_pos) else (100, 100, 100)
            pygame.draw.rect(screen, color, self.continue_btn_rect)
            pygame.draw.rect(screen, (255, 255, 255), self.continue_btn_rect, 3)
            
            cont_text = self.font_small.render("Continue", True, (255, 255, 255))
            screen.blit(cont_text, (self.continue_btn_rect.centerx - cont_text.get_width() // 2, self.continue_btn_rect.centery - cont_text.get_height() // 2))
        else:
            title_text = self.font_large.render("The Dark Altar", True, (200, 50, 50))
            screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 120))
            
            for btn in self.buttons:
                color = btn["hover_color"] if btn["rect"].collidepoint(mouse_pos) else btn["color"]
                pygame.draw.rect(screen, color, btn["rect"])
                pygame.draw.rect(screen, (255, 255, 255), btn["rect"], 3) # Border
                
                # Text rendering with word wrap for description
                lines = btn["text"].split('\n')
                y_offset = btn["rect"].y + 20
                for i, line in enumerate(lines):
                    if i >= 4: # Desc text, split further if needed or just use simple wrap
                        words = line.split(' ')
                        wrap_line = ""
                        for word in words:
                            test_line = wrap_line + word + " "
                            if self.font_small.size(test_line)[0] > self.button_width - 20:
                                text_surface = self.font_small.render(wrap_line, True, (200, 200, 200))
                                screen.blit(text_surface, (btn["rect"].centerx - text_surface.get_width() // 2, y_offset))
                                y_offset += 25
                                wrap_line = word + " "
                            else:
                                wrap_line = test_line
                        if wrap_line:
                            text_surface = self.font_small.render(wrap_line, True, (200, 200, 200))
                            screen.blit(text_surface, (btn["rect"].centerx - text_surface.get_width() // 2, y_offset))
                            y_offset += 25
                    else:
                        text_surface = self.font_small.render(line, True, (255, 255, 255))
                        screen.blit(text_surface, (btn["rect"].centerx - text_surface.get_width() // 2, y_offset))
                        y_offset += 30

    def handle_event(self, event: pygame.event.Event):
        """
        Handles events and returns the selected upgrade ID if clicked, 'CONTINUE' if continue clicked, else None.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if not self.available_upgrades:
                if self.continue_btn_rect.collidepoint(mouse_pos):
                    return "CONTINUE"
            else:
                for btn in self.buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        return btn["id"]
        return None
        
    def remove_upgrade(self, upgrade_id: int):
        self.available_upgrades = [u for u in self.available_upgrades if u["id"] != upgrade_id]
