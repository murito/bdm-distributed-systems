import pygame

class PacmanButton:
    def __init__(self, text, position, size=(200, 50), font_size=28, text_color=(255, 255, 0), bg_color=(0, 0, 0), border_color=(255, 255, 0), font_path=None):
        self.text = text
        self.position = position
        self.size = size
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.hovered = False

        # Fuente estilo arcade
        if font_path:
            self.font = pygame.font.Font(font_path, font_size)
        else:
            self.font = pygame.font.SysFont(None, font_size)

        self.rect = pygame.Rect(position, size)

    def draw(self, surface):
        # Cambia color si está en hover
        fill_color = (50, 50, 50) if self.hovered else self.bg_color
        pygame.draw.rect(surface, fill_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 3)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True  # Acción del botón
        return False
