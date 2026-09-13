import pygame

def draw_text_with_outline(screen, text, font, text_color, center_pos, outline_color=(0, 0, 0), shadow_offset=2):
    """
    Renders text with a 1px outline and a drop shadow, then draws the main text on top.
    """
    # Create the outline surfaces
    outline_surf = font.render(text, True, outline_color)
    x, y = center_pos
    
    # Draw drop shadow (slightly lower and to the right)
    shadow_rect = outline_surf.get_rect(center=(x + shadow_offset, y + shadow_offset))
    screen.blit(outline_surf, shadow_rect)
    
    # Draw 1px outline in 8 directions
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            outline_rect = outline_surf.get_rect(center=(x + dx, y + dy))
            screen.blit(outline_surf, outline_rect)
            
    # Draw the main text
    main_surf = font.render(text, True, text_color)
    main_rect = main_surf.get_rect(center=center_pos)
    screen.blit(main_surf, main_rect)

def draw_polished_button(screen, rect, text, font):
    """
    Draws a button with hover state. Handles visual changes directly based on mouse_pos.
    """
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    
    # Palette
    # Deep Charcoal (#1A1A1A is ~26,26,26) base, lighter on hover
    bg_color = (40, 40, 40, 220) if is_hovered else (26, 26, 26, 200) 
    # Solar-Gold (#FFD700) on hover, Bone-white (#E8E8E8) default
    border_color = (255, 215, 0) if is_hovered else (232, 232, 232) 
    text_color = (255, 215, 0) if is_hovered else (232, 232, 232)
    
    # Create a temporary surface for the background to support transparency.
    btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    btn_surf.fill(bg_color)
    screen.blit(btn_surf, rect.topleft)
    
    # Draw border
    pygame.draw.rect(screen, border_color, rect, 2)
    
    # Draw text with outline
    draw_text_with_outline(screen, text, font, text_color, rect.center)

def draw_slider(screen, rect, label, volume, small_font):
    """
    Draws an interactive slider.
    """
    # Draw label
    label_surf = small_font.render(label, True, (255, 255, 255))
    screen.blit(label_surf, (rect.x, rect.y - 25))
    
    # Draw background track
    pygame.draw.rect(screen, (50, 50, 50), rect)
    
    # Draw filled track
    fill_rect = pygame.Rect(rect.x, rect.y, int(rect.width * volume), rect.height)
    pygame.draw.rect(screen, (100, 150, 255), fill_rect)
    
    # Draw outline
    pygame.draw.rect(screen, (200, 200, 200), rect, 2)
    
    # Draw handle
    handle_x = rect.x + int(rect.width * volume)
    pygame.draw.circle(screen, (255, 255, 255), (handle_x, rect.centery), 12)
    
    # Draw percentage text
    pct_surf = small_font.render(f"{int(volume * 100)}%", True, (200, 200, 200))
    screen.blit(pct_surf, (rect.right + 15, rect.centery - pct_surf.get_height() // 2))
