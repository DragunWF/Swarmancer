import pygame
import os

class AssetLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetLoader, cls).__new__(cls)
            cls._instance._sprites = {}
            cls._instance._initialized = False
        return cls._instance

    def initialize(self, scale: float = 3.0, archer_tint: tuple = (100, 100, 255)):
        """Loads and pre-caches assets to prevent disk I/O during gameplay."""
        if self._initialized:
            return
            
        base_path = os.path.join("sprites", "skeleton")
        directions = ["east", "north-east", "north", "north-west", 
                      "west", "south-west", "south", "south-east"]
        
        for d in directions:
            path = os.path.join(base_path, f"{d}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                
                # Pre-scale the image
                w, h = img.get_size()
                scaled_img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
                
                # Store default variant
                self._sprites[f"skeleton_{d}_default"] = scaled_img
                
                # Create and store archer (tinted) variant
                archer_img = scaled_img.copy()
                archer_img.fill(archer_tint, special_flags=pygame.BLEND_MULT)
                self._sprites[f"skeleton_{d}_archer"] = archer_img
                
        self._initialized = True

    def get_sprite(self, sprite_ref: str, direction: str, variant: str = "default") -> pygame.Surface:
        """Retrieves a cached sprite surface."""
        key = f"{sprite_ref}_{direction}_{variant}"
        return self._sprites.get(key)
