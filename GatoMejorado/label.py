import pygame

class Label:
    def __init__(self, text, color, position):
        self.text = text
        self.font = pygame.font.SysFont("Consolas", 18)
        self.color = color
        self.position = position
        self.render = self.font.render(self.text, True, self.color)

    def draw(self, screen):
        screen.blit(self.render, self.position)

    def update(self, nuevo_text):
        self.text = nuevo_text
        self.render = self.font.render(self.text, True, self.color)