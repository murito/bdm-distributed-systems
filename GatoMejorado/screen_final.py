import pygame

class ScreenFinal:
    def __init__(self, screen, gato):
        print("Initializing Final screen")
        self.x_wins = None
        self.o_wins = None
        self.draw = None
        self.screen = screen
        self.gato = gato

    def on_init(self):
        self.x_wins = pygame.image.load("images/x_wins.png").convert_alpha()
        self.o_wins = pygame.image.load("images/o_wins.png").convert_alpha()
        self.draw = pygame.image.load("images/empate.png").convert_alpha()

    def on_event(self, event):
        pass

    def on_render(self):
        if self.gato.winner == 1:
            self.screen.blit(self.x_wins, (0, 0))

        if self.gato.winner == 2:
            self.screen.blit(self.o_wins, (0, 0))

        if self.gato.winner == 3:
            self.screen.blit(self.draw, (0, 0))

        if self.gato.winner == 1 or self.gato.winner == 2:
            self.gato.label_turn.update(f"Congratulations player {'X' if (self.gato.winner == 1) else 'O'}")
        else:
            self.gato.label_turn.update(f"UPS! Tablas!")
