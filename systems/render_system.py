from systems.system import System
import pygame
import math
from utils.asset_loader import AssetLoader
from utils.math_utils import velocity_to_direction
from ui.ui_utils import draw_text_with_outline

class RenderSystem(System):
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 20)
        self.floating_font = pygame.font.SysFont(None, 24)

    def update(self, entities, dt):
        screen = pygame.display.get_surface()
        if not screen:
            return

        screen_width = screen.get_width()

        for entity in entities:
            if hasattr(entity, 'graphics') and hasattr(entity, 'transform'):
                gfx = entity.graphics
                pos = (int(entity.transform.x), int(entity.transform.y))
                
                scale_multiplier = 1.0
                if hasattr(entity, 'pulsing_animation'):
                    anim = entity.pulsing_animation
                    anim.time_elapsed += dt
                    scale_multiplier = 1.0 + (anim.amplitude * math.sin(anim.time_elapsed * anim.speed))
                
                if type(gfx).__name__ == 'TextGraphics':
                    if gfx.alpha < 255:
                        temp_surf = pygame.Surface((150, 50), pygame.SRCALPHA)
                        draw_text_with_outline(temp_surf, gfx.text, self.floating_font, gfx.color, (75, 25))
                        temp_surf.set_alpha(gfx.alpha)
                        screen.blit(temp_surf, temp_surf.get_rect(center=pos))
                    else:
                        draw_text_with_outline(screen, gfx.text, self.floating_font, gfx.color, pos)
                    continue

                if getattr(gfx, 'sprite_ref', None):
                    if hasattr(entity, 'physics'):
                        vx = entity.physics.velocity.x
                        vy = entity.physics.velocity.y
                        direction = velocity_to_direction(vx, vy)
                    else:
                        direction = "south"
                    
                    if scale_multiplier != 1.0:
                        sprite = AssetLoader().get_scaled_sprite(gfx.sprite_ref, direction, scale_multiplier)
                    else:
                        sprite = AssetLoader().get_sprite(gfx.sprite_ref, direction)
                        
                    if sprite:
                        # Blit centered
                        rect = sprite.get_rect(center=pos)
                        
                        # Apply alpha if needed
                        if hasattr(gfx, 'alpha') and gfx.alpha < 255:
                            sprite = sprite.copy()
                            sprite.set_alpha(gfx.alpha)
                            
                        screen.blit(sprite, rect)
                    else:
                        # Fallback if sprite is missing
                        if hasattr(gfx, 'alpha') and gfx.alpha < 255:
                            surf = pygame.Surface((int(gfx.scale)*2, int(gfx.scale)*2), pygame.SRCALPHA)
                            pygame.draw.circle(surf, (*gfx.color, gfx.alpha), (int(gfx.scale), int(gfx.scale)), int(gfx.scale))
                            rect = surf.get_rect(center=pos)
                            screen.blit(surf, rect)
                        else:
                            pygame.draw.circle(screen, gfx.color, pos, int(gfx.scale))
                else:
                    if hasattr(gfx, 'alpha') and gfx.alpha < 255:
                        surf = pygame.Surface((int(gfx.scale)*2, int(gfx.scale)*2), pygame.SRCALPHA)
                        pygame.draw.circle(surf, (*gfx.color, gfx.alpha), (int(gfx.scale), int(gfx.scale)), int(gfx.scale))
                        rect = surf.get_rect(center=pos)
                        screen.blit(surf, rect)
                    else:
                        pygame.draw.circle(screen, gfx.color, pos, int(gfx.scale))
                
            elif hasattr(entity, 'is_player'):
                pos = (int(entity.transform.x), int(entity.transform.y))
                pygame.draw.circle(screen, (255, 0, 0), pos, 5, 1)

        # --- Boomer Blast Radius Indicator ---
        # Draws a faint orange ring at the AoE radius so players can see the danger zone.
        for entity in entities:
            if getattr(entity, 'enemy_type', None) != 'boomer':
                continue
            if getattr(entity, 'marked_for_deletion', False):
                continue
            pos = (int(entity.transform.x), int(entity.transform.y))
            pygame.draw.circle(screen, (200, 120, 40), pos, int(entity.blast_radius), 1)

            if hasattr(entity, 'fuse_timer') and entity.fuse_timer.elapsed > 0:
                time_left = max(0.0, entity.fuse_timer.duration - entity.fuse_timer.elapsed)
                text_surf = self.font.render(f"{time_left:.1f}s", True, (255, 150, 50))
                text_rect = text_surf.get_rect(center=(pos[0], pos[1] - int(entity.graphics.scale) - 15))
                screen.blit(text_surf, text_rect)

        # --- LaserDrone Telegraph & Beam ---
        for entity in entities:
            if getattr(entity, 'enemy_type', None) != 'laser_drone':
                continue
            if not hasattr(entity, 'aiming_timer'):
                continue

            at = entity.aiming_timer
            drone_y = int(entity.transform.y)

            if not at.is_firing:
                # Telegraph phase: warning line grows from transparent to fully opaque
                charge_progress = at.elapsed / at.charge_duration  # 0.0 → 1.0
                alpha = int(255 * charge_progress)

                # Draw the warning line onto a transparent surface to support alpha
                warn_surface = pygame.Surface((screen_width, 2), pygame.SRCALPHA)
                warn_surface.fill((255, 220, 50, alpha))
                screen.blit(warn_surface, (0, drone_y - 1))
            else:
                # Firing phase: solid bright beam rectangle
                beam_rect = pygame.Rect(0, drone_y - int(entity.beam_width),
                                        screen_width, int(entity.beam_width) * 2)
                beam_surface = pygame.Surface((screen_width, int(entity.beam_width) * 2), pygame.SRCALPHA)
                beam_surface.fill((255, 255, 200, 210))
                screen.blit(beam_surface, beam_rect.topleft)

            if hasattr(entity, 'lifespan_timer'):
                time_left = max(0.0, entity.lifespan_timer.duration - entity.lifespan_timer.elapsed)
                text_surf = self.font.render(f"{time_left:.1f}s", True, (200, 200, 200))
                text_rect = text_surf.get_rect(center=(int(entity.transform.x), drone_y - int(entity.graphics.scale) - 15))
                screen.blit(text_surf, text_rect)
