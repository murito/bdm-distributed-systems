import pygame
from settings import *

class GameLogic:
    def __init__(self, game):
        self.game = game

    def find_spawn(self, board, offset_x, offset_y, tile_size):
        """
        Busca una celda abierta ('0') cerca del centro del tablero
        y devuelve coordenadas en píxeles (x, y).
        """
        rows = len(board)
        cols = len(board[0])

        center_r = rows // 2
        center_c = cols // 2

        # Radio de búsqueda alrededor del centro
        search_radius = max(rows, cols) // 4

        for dr in range(-search_radius, search_radius + 1):
            for dc in range(-search_radius, search_radius + 1):
                r = center_r + dr
                c = center_c + dc
                if 0 <= r < rows and 0 <= c < cols and board[r][c] == '0':
                    x = offset_x + c * tile_size + tile_size / 2
                    y = offset_y + r * tile_size + tile_size / 2
                    return x, y

        # Si no encuentra nada (raro), devuelve el centro por defecto
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
        """Verifica si algún jugador colisionó con otro."""
        for i, p1 in enumerate(scene.players):
            for j, p2 in enumerate(scene.players):
                if i >= j:
                    continue  # evita comparar el mismo par dos veces
                if p1.x == p2.x and p1.y == p2.y:
                    self.on_player_collision(p1, p2)

    def on_player_collision(self, player1, player2):
        """Acción al detectar una colisión entre jugadores."""

        if player1.is_evil and not player2.is_evil:
            print(f"{player2.id} fue atrapado por {player1.id}!")
        elif player2.is_evil and not player1.is_evil:
            print(f"{player1.id} fue atrapado por {player2.id}!")