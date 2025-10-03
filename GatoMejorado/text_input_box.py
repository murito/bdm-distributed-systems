import pygame

class TextInputBox:
    def __init__(self, x, y, w, h, label_text="", font_size=32, text_color=(255, 255, 255), box_color=(200, 200, 200), active_color=(30, 144, 255)):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = box_color
        self.color_active = active_color
        self.color = self.color_inactive
        self.text = ""
        self.font = pygame.font.Font(None, font_size)
        self.text_color = text_color
        self.active = False
        self.label_text = label_text
        self.label_surface = self.font.render(self.label_text, True, self.text_color)

        # Ajuste de posición del label a la izquierda
        self.label_offset_x = -self.label_surface.get_width() - 10
        self.label_offset_y = (self.rect.height - self.label_surface.get_height()) // 2

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                entered_text = self.text
                self.text = ""
                return entered_text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return None

    def update(self):
        width = max(200, self.font.size(self.text)[0] + 10)
        self.rect.w = width

    def draw(self, screen):
        # Dibujar etiqueta a la izquierda del campo
        label_x = self.rect.x + self.label_offset_x
        label_y = self.rect.y + self.label_offset_y
        screen.blit(self.label_surface, (label_x, label_y))

        # Dibujar campo de texto
        txt_surface = self.font.render(self.text, True, self.text_color)
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)
