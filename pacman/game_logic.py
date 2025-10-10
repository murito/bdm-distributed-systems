import pygame
from settings import *
from p2p_helpers import json_packet, packet_data, get_json_by_id, update_object_by_id
from p2p_node import broadcast_message, peer_players

class GameLogic:
    def __init__(self, game):
        self.game = game

    def find_spawn(self, board, offset_x, offset_y, tile_size):
        """
        Search for a open cell ('0') nearby the center of the board.
        and return the coords in pixels (x, y).
        """
        rows = len(board)
        cols = len(board[0])

        center_r = rows // 2
        center_c = cols // 2

        # Looking radius around the center
        search_radius = max(rows, cols) // 4

        for dr in range(-search_radius, search_radius + 1):
            for dc in range(-search_radius, search_radius + 1):
                r = center_r + dr
                c = center_c + dc
                if 0 <= r < rows and 0 <= c < cols and board[r][c] == '0':
                    x = offset_x + c * tile_size + tile_size / 2
                    y = offset_y + r * tile_size + tile_size / 2
                    return x, y

        # If there is nothing extrange returns the center by default
        x = offset_x + center_c * tile_size + tile_size / 2
        y = offset_y + center_r * tile_size + tile_size / 2
        return x, y

    def create_walls(self):
        walls = []
        for row_idx, row in enumerate(board):
            for col_idx, cell in enumerate(row):
                if cell == "1":
                    rect = pygame.Rect(
                        BOARD_OFFSET_X + col_idx * TILE_SIZE,
                        BOARD_OFFSET_Y + row_idx * TILE_SIZE,
                        TILE_SIZE, TILE_SIZE
                    )
                    walls.append(rect)
        return walls

    def draw_board(self,surface):
        for row_idx, row in enumerate(board):
            for col_idx, cell in enumerate(row):
                if cell == "1":
                    x = BOARD_OFFSET_X + col_idx * TILE_SIZE
                    y = BOARD_OFFSET_Y + row_idx * TILE_SIZE
                    # Dibujar sólo bordes azules entre celdas de camino
                    if row_idx > 0 and board[row_idx - 1][col_idx] == "0":
                        pygame.draw.line(surface, (0, 0, 255), (x, y), (x + TILE_SIZE, y), 2)
                    if row_idx < len(board) - 1 and board[row_idx + 1][col_idx] == "0":
                        pygame.draw.line(surface, (0, 0, 255), (x, y + TILE_SIZE), (x + TILE_SIZE, y + TILE_SIZE), 2)
                    if col_idx > 0 and row[col_idx - 1] == "0":
                        pygame.draw.line(surface, (0, 0, 255), (x, y), (x, y + TILE_SIZE), 2)
                    if col_idx < len(row) - 1 and row[col_idx + 1] == "0":
                        pygame.draw.line(surface, (0, 0, 255), (x + TILE_SIZE, y), (x + TILE_SIZE, y + TILE_SIZE), 2)


    def player_coin_collision(self, scene, player, posx, posy):
        cx, cy = scene.coin.position
        if (posx - (TILE_SIZE / 2)) == cx and (posy - (TILE_SIZE / 2)) == cy:
            # pacman becomes evil
            player.activate_evil_mode(7000)

            # Get the coin out of the scene
            scene.coin.set_position((-10, -10))

            # Timer to get the coin in scene again
            scene.coin_timer = 6000

    def check_player_collisions(self, scene):
        """Check if any player collide with other (with some margin)."""
        COLLISION_MARGIN = 2  # margin in pixels

        for i, p1 in enumerate(scene.players):
            for j, p2 in enumerate(scene.players):
                if i >= j:
                    continue  # vaoid compare the same pair two times

                # --- Distance calculus ---
                dx = p1.x - p2.x
                dy = p1.y - p2.y
                distance = (dx ** 2 + dy ** 2) ** 0.5

                # --- Effective collision radius ---
                collision_radius = p1.radius + p2.radius - COLLISION_MARGIN

                if distance <= collision_radius:
                    self.on_player_collision(scene, p1, p2)

    def on_player_collision(self, scene, player1, player2):
        """Action when a collision between players was detected."""

        if player1.is_evil and not player2.is_evil:
            self.defeat_player_and_transmit(player2, scene)
        elif player2.is_evil and not player1.is_evil:
            self.defeat_player_and_transmit(player1, scene)

    def defeat_player_and_transmit(self, player, scene):
        player.defeated = True
        scene.check_for_the_winner = True

        player_json = get_json_by_id(peer_players, player.id)

        # Send defeated user to the others
        defeated_player = json_packet(
            identifier=player.id,
            sender=scene.game.whoami,
            players=scene.game.players_joined,
            color=player_json[0]['color'],
            x=player_json[0]['x'],
            y=player_json[0]['y'],
            direction=player_json[0]['direction'],
            ip=player_json[0]['ip'],
            port=player_json[0]['port'],
            coin_pos=scene.coin.position,
            outgoing_player=False,
            defeated=True
        )
        update_object_by_id(
            data_list=peer_players,
            target_id=player.id,
            new_properties={"defeated": True}
        )
        pkt = packet_data(defeated_player)
        broadcast_message(pkt)
