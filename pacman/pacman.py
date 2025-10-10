import pygame
import math
from settings import *
from p2p_node import peer_players, broadcast_message, packet_data, update_object_by_id

class Pacman:
    def __init__(self, identifier, pacman, x, y, color=(255,255,0), tile_size=24, speed=3, radius=10, controlled_locally=True, defeated=False):
        self.id = identifier
        self.prevx = x
        self.prevy = y
        self.x = x
        self.y = y
        self.base_color = color      # color normal
        self.color = color
        self.tile_size = tile_size
        self.speed = speed
        self.radius = radius
        self.direction = "LEFT"
        self.next_direction = None
        self.mouth_angle = 0
        self.mouth_opening = True
        self.controlled_locally = controlled_locally
        self.pacman = pacman
        self.defeated = defeated  # 🧩 ahora se usa de verdad

        # --- NEW ATTRIBUTES ---
        self.is_evil = False
        self.evil_timer = 0
        self.evil_color = (255, 50, 50)
        self.evil_flash = False

    def activate_evil_mode(self, duration_ms=5000):
        if self.defeated:
            return
        self.is_evil = True
        self.evil_timer = duration_ms
        self.color = self.evil_color
        self.speed = self.speed + 0.5

    def update(self, keys, board):
        if self.defeated:
            return  # 💀 Dont move nor update anything, because your are death

        rows = len(board)
        cols = len(board[0])

        # --- Turn evil mode ---
        if self.is_evil:
            self.evil_timer -= self.pacman.clock.get_time()
            if self.evil_timer < 2000:
                self.evil_flash = not self.evil_flash
                self.color = self.evil_color if self.evil_flash else self.base_color
            if self.evil_timer <= 0:
                self.is_evil = False
                self.color = self.base_color
                self.speed -= 0.5

        if self.controlled_locally:
            # Read the desired direction
            if keys[pygame.K_LEFT]: self.next_direction = "LEFT"
            elif keys[pygame.K_RIGHT]: self.next_direction = "RIGHT"
            elif keys[pygame.K_UP]: self.next_direction = "UP"
            elif keys[pygame.K_DOWN]: self.next_direction = "DOWN"

            col = int((self.x - BOARD_OFFSET_X) // self.tile_size)
            row = int((self.y - BOARD_OFFSET_Y) // self.tile_size)
            center_x = BOARD_OFFSET_X + col * self.tile_size + self.tile_size / 2
            center_y = BOARD_OFFSET_Y + row * self.tile_size + self.tile_size / 2
            aligned = abs(self.x - center_x) < 1 and abs(self.y - center_y) < 1

            # change the direction if it is aligned
            if aligned and self.next_direction:
                dcol, drow = 0, 0
                if self.next_direction == "LEFT": dcol = -1
                if self.next_direction == "RIGHT": dcol = 1
                if self.next_direction == "UP": drow = -1
                if self.next_direction == "DOWN": drow = 1
                new_row = row + drow
                new_col = col + dcol
                if 0 <= new_row < rows and 0 <= new_col < cols and board[new_row][new_col] == '0':
                    self.direction = self.next_direction
                    self.next_direction = None
                    self.x = center_x
                    self.y = center_y

            # --- Normal or tele-transport movement ---
            dcol, drow = 0, 0
            if self.direction == "LEFT": dcol = -1
            if self.direction == "RIGHT": dcol = 1
            if self.direction == "UP": drow = -1
            if self.direction == "DOWN": drow = 1
            target_col = col + dcol
            target_row = row + drow

            tunnel_rows = [r for r in range(rows) if board[r][0] == '0' and board[r][cols - 1] == '0']

            if 0 <= target_row < rows and 0 <= target_col < cols and board[target_row][target_col] == '0':
                if self.direction == "LEFT": self.x -= self.speed
                if self.direction == "RIGHT": self.x += self.speed
                if self.direction == "UP": self.y -= self.speed
                if self.direction == "DOWN": self.y += self.speed
            else:
                if row in tunnel_rows and self.direction in ("LEFT", "RIGHT"):
                    if target_col < 0:
                        dest = cols - 1
                        while dest >= 0 and board[row][dest] != '0':
                            dest -= 1
                        if dest >= 0:
                            self.x = BOARD_OFFSET_X + dest * self.tile_size + self.tile_size / 2
                            self.y = center_y
                    elif target_col >= cols:
                        dest = 0
                        while dest < cols and board[row][dest] != '0':
                            dest += 1
                        if dest < cols:
                            self.x = BOARD_OFFSET_X + dest * self.tile_size + self.tile_size / 2
                            self.y = center_y
                    else:
                        self.x, self.y = center_x, center_y
                else:
                    self.x, self.y = center_x, center_y

            # --- Send position by the network ---
            if self.prevx != self.x or self.prevy != self.y:
                self.prevx, self.prevy = self.x, self.y
                cx, cy = self.pacman.coin_initial_position
                msg = {
                    "players": self.pacman.players_joined,
                    "id": self.pacman.whoami,
                    "from": self.pacman.whoami,
                    "x": self.x,
                    "y": self.y,
                    "direction": self.direction,
                    "outgoing_player": False,
                    "coin_initial_position": f"{cx},{cy}",
                    "is_evil": self.is_evil,
                    "defeated": self.defeated
                }
                update_object_by_id(peer_players, self.id, msg)
                broadcast_message(packet_data(msg))

        # --- Mouth animation ---
        delta_angle = 8 if self.is_evil else 5
        if self.mouth_opening:
            self.mouth_angle += delta_angle
            if self.mouth_angle >= 45:
                self.mouth_opening = False
        else:
            self.mouth_angle -= delta_angle
            if self.mouth_angle <= 0:
                self.mouth_opening = True

    def set_position(self, x, y, direction=None, is_evil=None):
        if not self.defeated:
            self.x = x
            self.y = y
            if direction:
                self.direction = direction
            if is_evil is not None:
                self.is_evil = is_evil
                self.color = self.evil_color if is_evil else self.base_color

    def draw(self, surface):
        # --- Body ---
        if self.defeated:
            body_color = (150, 150, 150)  # gris
        else:
            body_color = self.base_color

        # Mouth rotation
        if self.direction == "RIGHT": rotation = 0
        elif self.direction == "LEFT": rotation = math.pi
        elif self.direction == "UP": rotation = math.pi / 2
        else: rotation = -math.pi / 2

        points = [(self.x, self.y)]
        for angle in range(self.mouth_angle, 360 - self.mouth_angle + 1, 5):
            rad = math.radians(angle)
            rx = self.x + self.radius * math.cos(rad + rotation)
            ry = self.y - self.radius * math.sin(rad + rotation)
            points.append((rx, ry))
        pygame.draw.polygon(surface, body_color, points)

        # --- EYES ---
        eye_offset_x = self.radius * 0.4
        eye_offset_y = -self.radius * 0.5
        eye1_pos = (self.x - eye_offset_x, self.y + eye_offset_y)
        eye2_pos = (self.x + eye_offset_x, self.y + eye_offset_y)

        if self.defeated:
            # 💀 Death eyes “X”
            self._draw_dead_eye(surface, eye1_pos)
            self._draw_dead_eye(surface, eye2_pos)
            return

        if self.is_evil:
            r, g, b = body_color
            brightness = (0.299 * r + 0.587 * g + 0.114 * b)
            if brightness > 128:
                evil_eye_color = (180, 0, 0)
            elif r > g and r > b:
                evil_eye_color = (0, 255, 255)
            elif g > r and g > b:
                evil_eye_color = (255, 0, 255)
            elif b > r and b > g:
                evil_eye_color = (255, 255, 0)
            else:
                evil_eye_color = (255, 0, 0)

            pygame.draw.circle(surface, evil_eye_color, eye1_pos, 3)
            pygame.draw.circle(surface, evil_eye_color, eye2_pos, 3)

            brow_offset_y = -6
            pygame.draw.line(surface, evil_eye_color,
                             (eye1_pos[0] - 3, eye1_pos[1] + brow_offset_y),
                             (eye1_pos[0] + 3, eye1_pos[1] + brow_offset_y - 2), 2)
            pygame.draw.line(surface, evil_eye_color,
                             (eye2_pos[0] - 3, eye2_pos[1] + brow_offset_y - 2),
                             (eye2_pos[0] + 3, eye2_pos[1] + brow_offset_y), 2)
        else:
            pygame.draw.circle(surface, (0, 0, 0), eye1_pos, 3)
            pygame.draw.circle(surface, (0, 0, 0), eye2_pos, 3)

    def _draw_dead_eye(self, surface, pos):
        """Draw a X like a death eye"""
        x, y = pos
        size = 4
        pygame.draw.line(surface, (0, 0, 0), (x - size, y - size), (x + size, y + size), 2)
        pygame.draw.line(surface, (0, 0, 0), (x - size, y + size), (x + size, y - size), 2)
