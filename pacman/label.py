import pygame

class Label:
    def __init__(self, text, position, font_size=32, color=(255, 255, 0), bg_color=(0, 0, 0), font_path=None, is_visible=True):
        self.text = text
        self.position = position
        self.font_size = font_size
        self.color = color
        self.bg_color = bg_color
        self.is_visible = is_visible

        # Fuente estilo arcade (puedes usar una fuente .ttf personalizada tipo pixel o retro)
        if font_path:
            self.font = pygame.font.Font(font_path, font_size)
        else:
            self.font = pygame.font.SysFont(None, font_size)  # Usa una fuente retro si está instalada

        self.rendered_text = self.font.render(self.text, True, self.color, self.bg_color)
        self.rect = self.rendered_text.get_rect(topleft=self.position)

    def draw(self, surface):
        if self.is_visible:
            surface.blit(self.rendered_text, self.rect)

    def update_text(self, new_text):
        self.text = new_text
        self.rendered_text = self.font.render(self.text, True, self.color, self.bg_color)
        self.rect = self.rendered_text.get_rect(topleft=self.position)

    def set_visible(self, visible: bool):
        """Cambia la visibilidad del label"""
        self.is_visible = visible