import pygame
from utils.state import GameState

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
_COLS = 3               # Grid columns
_CARD_W = 200           # Card width  (px)
_CARD_H = 240           # Card height (px)
_CARD_PAD = 20          # Horizontal padding between cards
_CARD_ROW_PAD = 20      # Vertical padding between rows

# Tooltip dimensions
_TIP_W = 260
_TIP_PAD = 12
_TIP_OFFSET_X = 16
_TIP_OFFSET_Y = 16

# Colors
_COL_OVERLAY        = (10, 5, 20, 185)
_COL_TITLE          = (210, 55, 55)
_COL_SOULS          = (255, 215, 0)
_COL_CARD_IDLE      = (35, 20, 50)
_COL_CARD_HOVER     = (60, 35, 80)
_COL_CARD_PURCHASED = (28, 28, 28)
_COL_BORDER         = (120, 70, 180)
_COL_BORDER_HOVER   = (200, 140, 255)
_COL_BORDER_PURCH   = (55, 55, 55)
_COL_COST           = (255, 215, 0)
_COL_COST_UNAFFORD  = (180, 60, 60)
_COL_DESC           = (190, 175, 210)
_COL_PURCH_LABEL    = (100, 100, 100)
_COL_TOOLTIP_BG     = (20, 12, 35, 230)
_COL_TOOLTIP_BORDER = (160, 100, 255)
_COL_TOOLTIP_TEXT   = (230, 220, 255)
_COL_CONTINUE_IDLE  = (40, 25, 60)
_COL_CONTINUE_HOVER = (70, 45, 100)
_COL_CONTINUE_BORDER= (180, 130, 255)
_COL_WHITE          = (255, 255, 255)


def _wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """Split *text* into lines that fit within *max_width* pixels."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class ShopController:
    """MVC controller for the Dark Altar shop overlay.

    Behaviour:
    - Renders all upgrades simultaneously in a responsive grid.
    - Purchased upgrades are flagged (`is_purchased`) and kept in the list,
      displayed with a gray-out tint and disabled click detection.
    - The player may purchase multiple upgrades per shop phase.
    - The shop closes only when the player explicitly clicks "Continue".
    - Hovering over an upgrade shows a floating tooltip with its description.
    """

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.font_title   = pygame.font.SysFont(None, 54)
        self.font_name    = pygame.font.SysFont(None, 28)
        self.font_small   = pygame.font.SysFont(None, 22)
        self.font_cost    = pygame.font.SysFont(None, 25)
        self.font_label   = pygame.font.SysFont(None, 20)

        self.all_upgrades: list[dict] = [
            {"id": 0, "name": "Skeletal Archers",     "desc": "Mutate ranged units to autonomously shoot down the charging peasant militia.",    "cost": 10},
            {"id": 1, "name": "Grave Robber's Yield", "desc": "Multiply the number of skeleton minions resurrected at each glowing grave.",       "cost": 15},
            {"id": 2, "name": "Evasion Mastery",      "desc": "Lower scatter cooldown to rapidly escape a stationary stone wizard tower.",        "cost": 15},
            {"id": 3, "name": "Bone Shrapnel",        "desc": "Minions shatter upon death, dealing splash damage to the charging peasant militia.","cost": 20},
            {"id": 4, "name": "Necrotic Momentum",    "desc": "Increase top speed so the swarm can condense and evade dwarf sapper bombs faster.","cost": 20},
            {"id": 5, "name": "Plague Wizard",        "desc": "Mutate units to cast plague bombs that detonate into toxic AoE blasts upon hitting an enemy.","cost": 25},
        ]

        # Each entry in available_upgrades is a dict copy with an extra
        # `is_purchased` boolean.  We never remove items — we only flag them.
        self.available_upgrades: list[dict] = []

        # Pre-computed card rects and the continue button rect.
        self._card_rects: list[pygame.Rect] = []
        self._continue_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

        self.refresh_upgrades()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def refresh_upgrades(self) -> None:
        """Called each time the shop opens.  Resets purchase flags for the
        current `available_upgrades` pool without re-randomising the list."""
        # Preserve which upgrades have been permanently removed from the pool
        # across sessions (handled by remove_upgrade), but reset is_purchased
        # visual flags so the grid is drawn fresh each visit.
        for upg in self.available_upgrades:
            upg["is_purchased"] = False
        self._compute_layout()

    def remove_upgrade(self, upgrade_id: int) -> None:
        """Permanently remove an upgrade from the pool (called after purchase
        to enforce the single-purchase rule)."""
        self.available_upgrades = [u for u in self.available_upgrades if u["id"] != upgrade_id]
        self._compute_layout()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def draw(self, screen: pygame.Surface, souls: int) -> None:
        """Draw the full shop overlay onto *screen*."""
        mouse_pos = pygame.mouse.get_pos()

        # Semi-transparent background overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(_COL_OVERLAY)
        screen.blit(overlay, (0, 0))

        # Title
        has_any_available = any(not u["is_purchased"] for u in self.available_upgrades)
        title_str = "The Dark Altar" if has_any_available else "The Dark Altar is Dormant"
        title_surf = self.font_title.render(title_str, True, _COL_TITLE)
        screen.blit(title_surf, (self.screen_width // 2 - title_surf.get_width() // 2, 40))

        # Souls counter
        souls_surf = self.font_name.render(f"Souls: {souls}", True, _COL_SOULS)
        screen.blit(souls_surf, (self.screen_width // 2 - souls_surf.get_width() // 2, 100))

        # Draw upgrade cards
        hovered_upgrade: dict | None = None
        for upg, rect in zip(self.available_upgrades, self._card_rects):
            purchased = upg["is_purchased"]
            hovering  = (not purchased) and rect.collidepoint(mouse_pos)
            affordable = souls >= upg["cost"]

            if hovering:
                hovered_upgrade = upg

            self._draw_card(screen, upg, rect, purchased, hovering, affordable)

        # Always-visible Continue button
        self._draw_continue_button(screen, mouse_pos)

        # Floating tooltip (drawn last so it sits on top)
        if hovered_upgrade is not None:
            self._draw_tooltip(screen, hovered_upgrade, mouse_pos, souls)

    def _draw_card(
        self,
        screen: pygame.Surface,
        upg: dict,
        rect: pygame.Rect,
        purchased: bool,
        hovering: bool,
        affordable: bool,
    ) -> None:
        # Background fill
        if purchased:
            fill_color   = _COL_CARD_PURCHASED
            border_color = _COL_BORDER_PURCH
        elif hovering:
            fill_color   = _COL_CARD_HOVER
            border_color = _COL_BORDER_HOVER
        else:
            fill_color   = _COL_CARD_IDLE
            border_color = _COL_BORDER

        pygame.draw.rect(screen, fill_color,   rect, border_radius=8)
        pygame.draw.rect(screen, border_color, rect, width=2, border_radius=8)

        if purchased:
            # Gray-out tint overlay
            tint = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            tint.fill((0, 0, 0, 120))
            screen.blit(tint, rect.topleft)

        # Upgrade name
        name_color = _COL_PURCH_LABEL if purchased else _COL_WHITE
        name_surf  = self.font_name.render(upg["name"], True, name_color)
        screen.blit(name_surf, (rect.centerx - name_surf.get_width() // 2, rect.y + 18))

        # Divider
        div_y = rect.y + 18 + name_surf.get_height() + 8
        div_color = _COL_BORDER_PURCH if purchased else _COL_BORDER
        pygame.draw.line(screen, div_color, (rect.x + 16, div_y), (rect.right - 16, div_y), 1)

        # Description (word-wrapped)
        desc_lines = _wrap_text(upg["desc"], self.font_small, rect.width - 24)
        desc_color = (70, 70, 70) if purchased else _COL_DESC
        y = div_y + 12
        for line in desc_lines:
            surf = self.font_small.render(line, True, desc_color)
            screen.blit(surf, (rect.x + 12, y))
            y += surf.get_height() + 4

        # Cost / status label at bottom of card
        if purchased:
            label_surf = self.font_cost.render("ACQUIRED", True, _COL_PURCH_LABEL)
            screen.blit(label_surf, (rect.centerx - label_surf.get_width() // 2, rect.bottom - 36))
        else:
            cost_color = _COL_COST if affordable else _COL_COST_UNAFFORD
            cost_surf  = self.font_cost.render(f"{upg['cost']} Souls", True, cost_color)
            screen.blit(cost_surf, (rect.centerx - cost_surf.get_width() // 2, rect.bottom - 36))

    def _draw_continue_button(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        hovering = self._continue_rect.collidepoint(mouse_pos)
        fill   = _COL_CONTINUE_HOVER if hovering else _COL_CONTINUE_IDLE
        border = _COL_CONTINUE_BORDER

        pygame.draw.rect(screen, fill,   self._continue_rect, border_radius=6)
        pygame.draw.rect(screen, border, self._continue_rect, width=2, border_radius=6)

        label = self.font_name.render("Continue", True, _COL_WHITE)
        screen.blit(label, (
            self._continue_rect.centerx - label.get_width()  // 2,
            self._continue_rect.centery - label.get_height() // 2,
        ))

    def _draw_tooltip(
        self,
        screen: pygame.Surface,
        upg: dict,
        mouse_pos: tuple[int, int],
        souls: int,
    ) -> None:
        lines = _wrap_text(upg["desc"], self.font_small, _TIP_W - _TIP_PAD * 2)
        line_h = self.font_small.get_height() + 4

        tip_h  = _TIP_PAD * 2 + self.font_name.get_height() + 8 + len(lines) * line_h + 28
        tip_x  = mouse_pos[0] + _TIP_OFFSET_X
        tip_y  = mouse_pos[1] + _TIP_OFFSET_Y

        # Clamp so the tooltip never overflows the screen
        tip_x = min(tip_x, self.screen_width  - _TIP_W - 4)
        tip_y = min(tip_y, self.screen_height - tip_h  - 4)

        tip_rect = pygame.Rect(tip_x, tip_y, _TIP_W, tip_h)

        tip_surf = pygame.Surface((_TIP_W, tip_h), pygame.SRCALPHA)
        tip_surf.fill(_COL_TOOLTIP_BG)
        screen.blit(tip_surf, tip_rect.topleft)
        pygame.draw.rect(screen, _COL_TOOLTIP_BORDER, tip_rect, width=2, border_radius=6)

        # Name
        name_surf = self.font_name.render(upg["name"], True, _COL_WHITE)
        screen.blit(name_surf, (tip_x + _TIP_PAD, tip_y + _TIP_PAD))

        # Description lines
        ty = tip_y + _TIP_PAD + self.font_name.get_height() + 8
        for line in lines:
            surf = self.font_small.render(line, True, _COL_TOOLTIP_TEXT)
            screen.blit(surf, (tip_x + _TIP_PAD, ty))
            ty += line_h

        # Cost line
        affordable = souls >= upg["cost"]
        cost_color = _COL_COST if affordable else _COL_COST_UNAFFORD
        cost_label = f"Cost: {upg['cost']} Souls" + ("" if affordable else "  (insufficient)")
        cost_surf  = self.font_label.render(cost_label, True, cost_color)
        screen.blit(cost_surf, (tip_x + _TIP_PAD, ty + 4))

    # ------------------------------------------------------------------
    # Event Handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> str | int | None:
        """Process a Pygame event.

        Returns:
            ``"CONTINUE"`` — player clicked the Continue button.
            ``int``        — upgrade ID of a valid (unpurchased) card click.
            ``None``       — no actionable result.
        """
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        mouse_pos = event.pos

        # Continue button — always active
        if self._continue_rect.collidepoint(mouse_pos):
            return "CONTINUE"

        # Upgrade card clicks — skip purchased cards
        for upg, rect in zip(self.available_upgrades, self._card_rects):
            if upg["is_purchased"]:
                continue
            if rect.collidepoint(mouse_pos):
                return upg["id"]

        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_layout(self) -> None:
        """Pre-compute card Rect objects for the current upgrade list and
        position the Continue button below the grid."""
        n = len(self.available_upgrades)
        if n == 0:
            self._card_rects = []
            self._continue_rect = pygame.Rect(
                self.screen_width // 2 - 110,
                self.screen_height // 2 - 30,
                220, 55
            )
            return

        cols = min(_COLS, n)
        rows = (n + cols - 1) // cols

        grid_w = cols * _CARD_W + (cols - 1) * _CARD_PAD
        grid_h = rows * _CARD_H + (rows - 1) * _CARD_ROW_PAD

        # Vertically centre the grid with room for title (≈130px) and
        # the Continue button below (≈70px).
        grid_top  = max(130, (self.screen_height - grid_h - 70) // 2)
        grid_left = (self.screen_width - grid_w) // 2

        self._card_rects = []
        for i, _ in enumerate(self.available_upgrades):
            row = i // cols
            col = i %  cols
            x = grid_left + col * (_CARD_W + _CARD_PAD)
            y = grid_top  + row * (_CARD_H + _CARD_ROW_PAD)
            self._card_rects.append(pygame.Rect(x, y, _CARD_W, _CARD_H))

        # Continue button centred below the grid, clamped to bottom of screen
        btn_y = min(grid_top + grid_h + 18, self.screen_height - 60)
        self._continue_rect = pygame.Rect(
            self.screen_width // 2 - 110,
            btn_y,
            220, 50
        )
