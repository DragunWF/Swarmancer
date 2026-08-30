class Graphics:
    def __init__(self, color: tuple, scale: float = 1.0, sprite_ref: str = ""):
        self.color = color
        self.scale = scale
        self.sprite_ref = sprite_ref
        self.alpha = 255
