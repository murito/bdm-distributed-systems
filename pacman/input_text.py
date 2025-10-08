import pygame

class TextInputWithLabel:
    def __init__(self, label_text, position, width=300, font_size=32, text_color=(255, 255, 0), bg_color=(0, 0, 0), font_path=None):
        self.label_text = label_text
        self.position = position
        self.width = width
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color
        self.active = False
        self.text = ""

        # Fuente estilo arcade
        if font_path:
            self.font = pygame.font.Font(font_path, font_size)
        else:
            self.font = pygame.font.SysFont(None, font_size)

        self.label_surface = self.font.render(self.label_text, True, self.text_color)
        self.label_rect = self.label_surface.get_rect(topleft=position)
        self.label_rect.y = self.label_rect.y + 5

        input_x = self.label_rect.right + 10
        self.input_rect = pygame.Rect(input_x, position[1], width, font_size)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.input_rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                if len(self.text) < 20:
                    self.text += event.unicode

    def draw(self, surface):
        # Dibuja el label
        surface.blit(self.label_surface, self.label_rect)

        # Dibuja el campo de texto
        pygame.draw.rect(surface, self.bg_color, self.input_rect)
        pygame.draw.rect(surface, self.text_color, self.input_rect, 2)

        text_surface = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
