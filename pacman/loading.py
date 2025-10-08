import pygame
import math

class PacmanLoadingAnimation:
    def __init__(self, screen_size=(600, 600), pacman_radius=40, num_dots=5, font_path=None):
        self.screen_size = screen_size
        self.pacman_radius = pacman_radius
        self.num_dots = num_dots
        self.angle = 0
        self.opening = True

        self.pacman_center = (screen_size[0] // 2, screen_size[1] // 2)
        self.pacman_color = (255, 255, 0)
        self.dot_color = (255, 255, 255)
        self.dot_radius = 5
        self.dot_spacing = 40
        self.dots = [(self.pacman_center[0] + 60 + i * self.dot_spacing, self.pacman_center[1]) for i in range(num_dots)]

        if font_path:
            self.font = pygame.font.Font(font_path, 20)
        else:
            self.font = pygame.font.SysFont(None, 20)

    def update(self):
        if self.opening:
            self.angle += 2
            if self.angle >= 45:
                self.opening = False
        else:
            self.angle -= 2
            if self.angle <= 5:
                self.opening = True

    def draw(self, surface):
        surface.fill((0, 0, 0))

        # Dibuja Pac-Man como un sector circular
        start_angle = math.radians(self.angle)
        end_angle = math.radians(360 - self.angle)
        points = [self.pacman_center]
        for a in range(self.angle, 360 - self.angle):
            x = self.pacman_center[0] + self.pacman_radius * math.cos(math.radians(a))
            y = self.pacman_center[1] + self.pacman_radius * math.sin(math.radians(a))
            points.append((x, y))
        pygame.draw.polygon(surface, self.pacman_color, points)

        # Dibuja los puntos
        for dot in self.dots:
            pygame.draw.circle(surface, self.dot_color, dot, self.dot_radius)

        # Texto de espera
        text_surface = self.font.render("WAITING FOR PLAYERS...", True, (0, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen_size[0] // 2, self.screen_size[1] - 100))
        surface.blit(text_surface, text_rect)
