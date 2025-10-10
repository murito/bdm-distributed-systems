import json
import random
import pygame

from settings import *
from label import Label
from pacman_button import PacmanButton
from input_text import TextInputWithLabel
from ghost_button import StylizedGhostButton
from loading import PacmanLoadingAnimation
from p2p_node import *
from p2p_helpers import get_json_by_field
from pacman import Pacman
from coin import Coin
from game_logic import GameLogic

# Base Scene
class Scene:
    def __init__(self, game):
        self.game = game

    def events(self, events):
        raise NotImplementedError("events must be defined")

    def update(self, dt):
        raise NotImplementedError("update must be defined")

    def draw(self, display):
        raise NotImplementedError("draw must be defined")

# Main Scene
class MainScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        game.display.fill((0, 0, 0))

        self.title_label = Label("PACMAN", position=(210, 80), font_size=30, font_path="pac-font.ttf")
        self.btn_server = PacmanButton("START A SERVER", position=(200, 200))
        self.btn_connect = PacmanButton("CONNECT", position=(200, 270))
        self.btn_test = PacmanButton("TEST", position=(200, 340))

    def events(self, events):
        for event in events:
            if self.btn_server.handle_event(event):
                self.game.change_scene(StartServerScene(self.game))

            if self.btn_connect.handle_event(event):
                self.game.change_scene(ConnectToServerScene(self.game))

            if self.btn_test.handle_event(event):
                self.game.change_scene(GameScene(self.game))

    def update(self, dt):
        pass

    def draw(self, display):
        self.title_label.draw(display)
        self.btn_server.draw(display)
        self.btn_connect.draw(display)
        self.btn_test.draw(display)

# Start a server
class StartServerScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        game.display.fill((0, 0, 0))

        self.title_label = Label("PACMAN", position=(210, 80), font_size=30, font_path="pac-font.ttf")

        self.port_field = TextInputWithLabel("PORT:", position=(200, 200), width=100, font_size=28)
        self.btn_start = PacmanButton("START", position=(200, 250))
        self.btn_back = StylizedGhostButton("BACK", size=(70, 60), position=(10, 465),
                                            ghost_color=(0, 255, 255), text_color=(0, 0, 0))  # Inky

        self.port_field.text = '8080'

    def events(self, events):
        for event in events:
            self.port_field.handle_event(event)

            if self.btn_start.handle_event(event):
                if self.port_field.text:
                    self.game.change_scene(WaitingPeersScene(self.game))

                    thread = threading.Thread(target=start_server, args=(int(self.port_field.text), self.game), daemon=True)
                    thread.start()

            if self.btn_back.handle_event(event):
                self.game.change_scene(MainScene(self.game))

    def update(self, dt):
        pass

    def draw(self, display):
        self.title_label.draw(display)
        self.port_field.draw(display)
        self.btn_start.draw(display)
        self.btn_back.draw(display)

#Connect to Server
class ConnectToServerScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        game.display.fill((0, 0, 0))

        self.title_label = Label("PACMAN", position=(210, 80), font_size=30, font_path="pac-font.ttf")

        self.ip_field = TextInputWithLabel("IP:", position=(200, 200), width=200, font_size=28)
        self.port_field = TextInputWithLabel("PORT:", position=(200, 250), width=100, font_size=28)
        self.btn_play = PacmanButton("PLAY", position=(200, 300))
        self.btn_back = StylizedGhostButton("BACK", size=(70, 60), position=(10, 465), ghost_color=(255, 184, 255))  # Pinky

        self.ip_field.text = '127.0.0.1'
        self.port_field.text = '8080'

    def events(self, events):
        for event in events:
            self.ip_field.handle_event(event)
            self.port_field.handle_event(event)

            if self.btn_play.handle_event(event):
                if self.ip_field.text and self.port_field.text:
                    #connect to server
                    connect_to_peer(str(self.ip_field.text), int(self.port_field.text), self.game)

                    # wait until 4 players join
                    self.game.change_scene(WaitingPeersScene(self.game))

            if self.btn_back.handle_event(event):
                self.game.change_scene(MainScene(self.game))

    def update(self, dt):
        pass

    def draw(self, display):
        self.title_label.draw(display)
        self.ip_field.draw(display)
        self.port_field.draw(display)
        self.btn_play.draw(display)
        self.btn_back.draw(display)

# Loading new connections
class WaitingPeersScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        game.display.fill((0, 0, 0))

        # Loading ...
        self.pacman_animation = PacmanLoadingAnimation()
        self.players_joined_label = Label("Players: 1", position=(250, 100), font_size=30)
        self.min_player = Label("Min players: 4", position=(250, 130), font_size=20, color=(255, 255, 255))

    def events(self, events):
        pass

    def update(self, dt):
        self.players_joined_label.update_text(f"Players: {self.game.players_joined}")
        self.pacman_animation.update()

        if self.game.players_joined >= MIN_PLAYERS:
            self.game.change_scene(GameScene(self.game))

    def draw(self, display):
        self.pacman_animation.draw(display)
        self.players_joined_label.draw(display)
        self.min_player.draw(display)

# Game scene
class GameScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        game.display.fill((0, 0, 0))

        # General logic for this scene
        self.game_logic = GameLogic(game)

        self.check_for_the_winner = False

        # Title
        self.title_label = Label("PACMAN", position=(210, 25), font_size=30, font_path="pac-font.ttf")
        self.defeated_label = Label("DERROTADO!", position=(160, 280), font_size=30, font_path="pac-font.ttf", is_visible=False)
        self.winner_label = Label("GANASTE!", position=(190, 280), font_size=30, font_path="pac-font.ttf",
                                    is_visible=False)

        # get x and y to position  players
        start_x, start_y = self.game_logic.find_spawn(board, BOARD_OFFSET_X, BOARD_OFFSET_Y, TILE_SIZE)

        self.coin_timer = None

        # instances of players
        self.players = []
        self.players_rendered = []
        for player in range(len(peer_players)):
            self.players_rendered.append(peer_players[player]['id'])

            # Everyone start at the same point
            peer_players[player]['x'] = start_x
            peer_players[player]['y'] = start_y

            r,g,b=peer_players[player]['color'].split(',')
            p = Pacman(peer_players[player]['id'], self.game, start_x, start_y, color=(int(r),int(g),int(b)), speed=2, controlled_locally=(peer_players[player]['id']==self.game.whoami) )
            self.players.append(p)

        # Coin
        self.coin = Coin(self.game, tile_size=24, board_offset_x=BOARD_OFFSET_X, board_offset_y=BOARD_OFFSET_Y)
        self.coin.set_position(self.game.coin_initial_position)

    def events(self, events):
        pass

    def update(self, dt):
        if self.game.players_joined < MIN_PLAYERS:
            self.game.change_scene(WaitingPeersScene(self.game))

        # update coin if it has changed its position
        cx, cy = self.coin.position
        if self.game.coin_initial_position != (cx, cy):
            self.coin.set_position(self.game.coin_initial_position)

        # remove player that left the game
        for player in self.players_rendered:
            if not player_exists(peer_players, player):
                self.players = [obj for obj in self.players if obj.id != player]

        # Add new players dynamically
        for player in range(len(peer_players)):
            if peer_players[player]['id'] not in self.players_rendered:
                start_x, start_y = self.game_logic.find_spawn(board, BOARD_OFFSET_X, BOARD_OFFSET_Y, TILE_SIZE)

                # Everyone start at the same point
                if peer_players[player]['x'] == 0 and peer_players[player]['y'] == 0:
                    peer_players[player]['x'] = start_x
                    peer_players[player]['y'] = start_y

                r, g, b = peer_players[player]['color'].split(',')
                p = Pacman(peer_players[player]['id'], self.game, start_x, start_y, color=(int(r), int(g), int(b)),
                           speed=2, controlled_locally=(peer_players[player]['id'] == self.game.whoami))
                self.players.append(p)
                self.players_rendered.append(peer_players[player]['id'])

        # loop over players
        for player in self.players:
            if player.defeated and self.game.whoami == player.id:
                self.defeated_label.set_visible(True)

            # Local player coin collision
            if player.controlled_locally:
                self.game_logic.player_coin_collision(self, player, player.x, player.y)

            # control remote players here
            if not player.controlled_locally:
                remote_data = get_json_by_id(peer_players, player.id)
                player.set_position(remote_data[0]['x'], remote_data[0]['y'], remote_data[0]['direction'])

                # remote player coin collision
                self.game_logic.player_coin_collision(self, player, int(remote_data[0]['x']), int(remote_data[0]['y']))

        # detect players collisions
        self.game_logic.check_player_collisions(self)

        # new place for coin
        if self.game.whoami == 'server':
            if self.coin_timer is not None:
                self.coin_timer -= self.game.clock.get_time()
                if self.coin_timer <= 0:
                    self.coin_timer = None
                    self.coin.place_random(board)

        # Check for the winner
        if self.check_for_the_winner:
            in_the_game = [obj for obj in peer_players if obj.get('defeated') is False]
            if len(in_the_game) == 1 and in_the_game[0]['id'] == self.game.whoami:
                self.winner_label.set_visible(True)

    def draw(self, display):
        display.fill((0, 0, 0))
        keys = pygame.key.get_pressed()

        # Add title
        self.title_label.draw(display)

        # draw the board
        self.game_logic.draw_board(display)

        # add players
        for player in self.players:
            player.update(keys, board)
            player.draw(display)

        # Add coin
        self.coin.update()
        self.coin.draw(display)

        self.defeated_label.draw(display)
        self.winner_label.draw(display)

        pygame.display.flip()