import pygame
from screen_one import ScreenOne
from screen_two import ScreenTwo
from screen_three import ScreenThree
from screen_game import ScreenGame
from screen_final import ScreenFinal
from label import Label
from p2p_node import peers

class Gato:
    def __init__(self):
        self._running = True
        self.screen = None
        self.size = self.weight, self.height = 512, 512
        self.background = None
        self.waiting_bg = None
        self.clock = None
        self.screen_one = None
        self.screen_two = None
        self.screen_three = None
        self.screen_game = None
        self.screen_final = None
        self.CURRENT_SCREEN = 0
        self.label_self_port = None
        self.label_remote_ip = None
        self.label_remote_port = None
        self.connection = [0,0,0]
        self.player = 0 # 1 - X, 2 - O
        self.label_player = None
        self.label_turn = None
        self.turn = False
        self.winner = 0
        self.game_state_bits = 0 ## Our data bits
        self.game_state = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]

    def on_init(self):
        pygame.init()
        pygame.display.set_caption("Gato # - Game")
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.background = pygame.image.load("images/background.png").convert()
        self.waiting_bg = pygame.image.load("images/waiting.png").convert_alpha()

        self.label_self_port = Label("Port:", (255, 255, 255), (10, 0))
        self.label_remote_ip = Label("Remote IP:", (255, 255, 255), (10, 20))
        self.label_remote_port = Label("Remote Port:" , (255, 255, 255), (10, 40))
        self.label_player = Label("Player:", (255, 255, 255), (10, 60))
        self.label_turn = Label("Turno:", (255, 255, 255), (10, 80))

        # screen 1
        self.screen_one = ScreenOne(self.screen, self)
        self.screen_one.on_init()

        # screen 2
        self.screen_two = ScreenTwo(self.screen, self)
        self.screen_two.on_init()

        # screen 3
        self.screen_three = ScreenThree(self.screen, self)
        self.screen_three.on_init()

        # screen game
        self.screen_game = ScreenGame(self.screen, self)
        self.screen_game.on_init()

        # final screen
        self.screen_final = ScreenFinal(self.screen, self)
        self.screen_final.on_init()

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

            print("Closing connections...")
            for peer in peers:
                peer.close()

        if self.CURRENT_SCREEN == 0:
            self.screen_one.on_event(event)

        if self.CURRENT_SCREEN == 1:
            self.screen_two.on_event(event)

        if self.CURRENT_SCREEN == 3:
            self.screen_game.on_event(event)

    def on_loop(self):
        pass

    def on_render(self):
        self.screen.blit(self.background, (0, 0))

        if self.CURRENT_SCREEN == 0 and self.winner == 0:
            self.screen_one.on_render()

        if self.CURRENT_SCREEN == 1 and self.winner == 0:
            self.screen_two.on_render()

        if self.CURRENT_SCREEN == 2 and self.winner == 0:
            self.screen_three.on_render()

        if self.CURRENT_SCREEN == 3 and self.winner == 0:
            self.screen_game.on_render()

        if  self.winner != 0:
            self.screen_final.on_render()

        self.label_self_port.draw(self.screen)
        self.label_remote_ip.draw(self.screen)
        self.label_remote_port.draw(self.screen)
        self.label_player.draw(self.screen)
        self.label_turn.draw(self.screen)

        self.clock.tick(30)
        pygame.display.flip()
        pass

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

if __name__ == "__main__":
    game = Gato()
    game.on_execute()