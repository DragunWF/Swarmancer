import pygame
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class AssetLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetLoader, cls).__new__(cls)
            cls._instance._sprites = {}
            cls._instance._background = None
            cls._instance._initialized = False
        return cls._instance

    def initialize(self, scale: float = 1.0):
        """Loads and pre-caches assets to prevent disk I/O during gameplay."""
        if self._initialized:
            return
            
        # Preload and scale background
        bg_path = os.path.join("sprites", "environment", "background.jpg")
        if os.path.exists(bg_path):
            bg_img = pygame.image.load(bg_path).convert()
            self._background = pygame.transform.smoothscale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

        sprite_refs = ["skeleton", "skeleton_archer", "grunt", "dwarf_sapper", "sun_wizard"]
        directions = ["east", "north-east", "north", "north-west", 
                      "west", "south-west", "south", "south-east"]
        
        for ref in sprite_refs:
            base_path = os.path.join("sprites", ref)
            for d in directions:
                path = os.path.join(base_path, f"{d}.png")
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    
                    # Pre-scale the image if not native scale
                    if scale != 1.0:
                        w, h = img.get_size()
                        scaled_img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
                    else:
                        scaled_img = img
                    
                    self._sprites[f"{ref}_{d}"] = scaled_img
                    
        # Load static pickups
        static_pickups = {
            "skeleton-spawn": ("skeleton_spawn_static", scale),
            "soul-drop": ("soul_drop_static", scale),
            "chalice": ("chalice_static", scale * 1.25)
        }
        
        for filename, (ref_key, pickup_scale) in static_pickups.items():
            pickup_path = os.path.join("sprites", "pickups", f"{filename}.png")
            if os.path.exists(pickup_path):
                img = pygame.image.load(pickup_path).convert_alpha()
                if pickup_scale != 1.0:
                    w, h = img.get_size()
                    scaled_img = pygame.transform.scale(img, (int(w * pickup_scale), int(h * pickup_scale)))
                else:
                    scaled_img = img
                self._sprites[ref_key] = scaled_img
                    
        self._initialized = True

    def get_sprite(self, sprite_ref: str, direction: str) -> pygame.Surface:
        """Retrieves a cached sprite surface."""
        key = f"{sprite_ref}_{direction}"
        return self._sprites.get(key)

    def get_scaled_sprite(self, sprite_ref: str, direction: str, scale_factor: float) -> pygame.Surface:
        """Retrieves a dynamically scaled sprite, caching the result to maintain 60 FPS."""
        # Discretize scale_factor to 2 decimal places to limit cache size
        rounded_scale = round(scale_factor, 2)
        base_key = f"{sprite_ref}_{direction}"
        cache_key = f"{base_key}_{rounded_scale:.2f}"
        
        if cache_key in self._sprites:
            return self._sprites[cache_key]
            
        base_sprite = self._sprites.get(base_key)
        if not base_sprite:
            return None
            
        w, h = base_sprite.get_size()
        scaled_sprite = pygame.transform.scale(base_sprite, (int(w * rounded_scale), int(h * rounded_scale)))
        self._sprites[cache_key] = scaled_sprite
        return scaled_sprite

    def get_background(self) -> pygame.Surface:
        """Retrieves the cached background surface."""
        return self._background
