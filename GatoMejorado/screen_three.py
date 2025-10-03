import pygame

class ScreenThree:
    def __init__(self, screen, gato):
        print("Initializing ScreenThree")
        self.connecting = None
        self.screen = screen
        self.gato = gato

    def on_init(self):
        self.connecting = pygame.image.load("images/conecting.png").convert_alpha()

    def on_event(self, event):
        pass

    def on_render(self):
        self.screen.blit(self.connecting, (126, 223))
