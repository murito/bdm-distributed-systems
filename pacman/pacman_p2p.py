import sys

import pygame as pg
from settings import *
from scenes import MainScene
from p2p_node import peers
from settings import board
from p2p_helpers import place_random

class PacmanP2P:
    def __init__(self):
        pg.init()
        pg.display.set_caption(CAPTION)
        self.display = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()

        # Game logic
        self.players_joined = 1
        self.network_packet = 0
        self.whoami = None
        self.my_color = None
        self.coin_initial_position = place_random(board)

        # Scenes
        self.scene = MainScene(self)

    def run(self):
        while 1:
            dt = self.clock.tick(FPS) / 1000
            ev = pg.event.get()  # new
            for event in ev:  # edited
                if event.type == pg.QUIT:
                    print("Closing connections...")
                    for peer in peers:
                        if peer:
                            peer.close()

                    sys.exit()
            # Scene events
            self.scene.events(ev)
            self.scene.update(dt)
            self.scene.draw(self.display)
            pg.display.update()

    def change_scene(self, scene):
        self.scene = scene

if __name__ == "__main__":
    game = PacmanP2P()
    game.run()