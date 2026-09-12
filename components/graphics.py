class Graphics:
    def __init__(self, color: tuple, scale: float = 1.0, sprite_ref: str = ""):
        self.color = color
        self.scale = scale
        self.sprite_ref = sprite_ref
        self.alpha = 255

class TextGraphics:
    def __init__(self, text: str, color: tuple, font_size: int = 24):
        self.text = text
        self.color = color
        self.font_size = font_size
        self.alpha = 255
