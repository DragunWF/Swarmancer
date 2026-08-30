from systems.system import System
import pygame

class RenderSystem(System):
    def update(self, entities, dt):
        screen = pygame.display.get_surface()
        if not screen:
            return

        screen_width = screen.get_width()

        for entity in entities:
            if hasattr(entity, 'graphics') and hasattr(entity, 'transform'):
                gfx = entity.graphics
                pos = (int(entity.transform.x), int(entity.transform.y))
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
