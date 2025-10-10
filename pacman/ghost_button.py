import pygame

"""
Blinky	(255, 0, 0)	El agresivo
Pinky	(255, 184, 255)	El emboscador
Inky	(0, 255, 255)	El impredecible
Clyde	(255, 165, 0)	El relajado
"""


class StylizedGhostButton:
    def __init__(self, text, position, size=(140, 120), font_size=22,
                 ghost_color=(255, 0, 0), eye_color=(255, 255, 255), pupil_color=(0, 0, 255),
                 text_color=(255, 255, 255), font_path=None):
        self.text = text
        self.position = position
        self.size = size
        self.ghost_color = ghost_color
        self.eye_color = eye_color
        self.pupil_color = pupil_color
        self.text_color = text_color
        self.hovered = False

        if font_path:
            self.font = pygame.font.Font(font_path, font_size)
        else:
            self.font = pygame.font.SysFont(None, font_size)

        self.rect = pygame.Rect(position, size)

    def draw(self, surface):
        x, y = self.position
        w, h = self.size

        # Shadow
        shadow_offset = 4
        shadow_rect = pygame.Rect(x + shadow_offset, y + shadow_offset, w, h)
        pygame.draw.ellipse(surface, (30, 30, 30), shadow_rect)

        # Ghost body
        pygame.draw.ellipse(surface, self.ghost_color, (x, y, w, h // 1.5))
        pygame.draw.rect(surface, self.ghost_color, (x, y + h // 3, w, h // 2))

        # Bottom waves
        foot_radius = w // 6
        for i in range(3):
            cx = x + foot_radius + i * foot_radius * 2
            cy = y + h
            pygame.draw.circle(surface, self.ghost_color, (cx, cy), foot_radius)

        # Big eyes
        eye_radius = 12
        eye_y = y + h // 4
        eye_x1 = x + w // 3 - 10
        eye_x2 = x + 2 * w // 3 - 10
        pygame.draw.circle(surface, self.eye_color, (eye_x1, eye_y), eye_radius)
        pygame.draw.circle(surface, self.eye_color, (eye_x2, eye_y), eye_radius)

        # Pupils
        pygame.draw.circle(surface, self.pupil_color, (eye_x1 + 4, eye_y + 2), 5)
        pygame.draw.circle(surface, self.pupil_color, (eye_x2 + 4, eye_y + 2), 5)

        # Text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2 + 10))
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
