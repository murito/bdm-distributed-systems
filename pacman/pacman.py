import pygame
import math
from settings import *
from p2p_node import peer_players, broadcast_message, packet_data, update_object_by_id

class Pacman:
    def __init__(self, identifier, pacman, x, y, color=(255,255,0), tile_size=24, speed=3, radius=10, controlled_locally=True):
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

        # --- NUEVOS ATRIBUTOS ---
        self.is_evil = False
        self.evil_timer = 0          # tiempo restante en ms
        self.evil_color = (255, 50, 50)
        self.evil_flash = False      # para animar parpadeo visual

    def activate_evil_mode(self, duration_ms=5000):
        """Activa el modo malvado por cierto tiempo (en milisegundos)."""
        self.is_evil = True
        self.evil_timer = duration_ms
        self.color = self.evil_color
        #print(f"Pacman {self.id} se ha vuelto MALVADO por {duration_ms/1000:.1f}s")

    def update(self, keys, board):
        rows = len(board)
        cols = len(board[0])

        # --- Actualizar temporizador del modo malvado ---
        if self.is_evil:
            self.evil_timer -= self.pacman.clock.get_time()  # get_time() = ms entre frames
            # Parpadea al final del tiempo
            if self.evil_timer < 2000:
                self.evil_flash = not self.evil_flash
                self.color = self.evil_color if self.evil_flash else self.base_color
            if self.evil_timer <= 0:
                self.is_evil = False
                self.color = self.base_color
                #print(f"Pacman {self.id} ha vuelto a la normalidad")

        if self.controlled_locally:
            # Leer dirección deseada
            if keys[pygame.K_LEFT]:
                self.next_direction = "LEFT"
            elif keys[pygame.K_RIGHT]:
                self.next_direction = "RIGHT"
            elif keys[pygame.K_UP]:
                self.next_direction = "UP"
            elif keys[pygame.K_DOWN]:
                self.next_direction = "DOWN"

            # Celda actual
            col = int((self.x - BOARD_OFFSET_X) // self.tile_size)
            row = int((self.y - BOARD_OFFSET_Y) // self.tile_size)
            center_x = BOARD_OFFSET_X + col * self.tile_size + self.tile_size / 2
            center_y = BOARD_OFFSET_Y + row * self.tile_size + self.tile_size / 2
            aligned = abs(self.x - center_x) < 1 and abs(self.y - center_y) < 1

            # Cambiar dirección si está alineado
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

            # Intentar mover en la dirección actual
            dcol, drow = 0, 0
            if self.direction == "LEFT": dcol = -1
            if self.direction == "RIGHT": dcol = 1
            if self.direction == "UP": drow = -1
            if self.direction == "DOWN": drow = 1
            target_col = col + dcol
            target_row = row + drow

            if 0 <= target_row < rows and 0 <= target_col < cols and board[target_row][target_col] == '0':
                if self.direction == "LEFT": self.x -= self.speed
                if self.direction == "RIGHT": self.x += self.speed
                if self.direction == "UP": self.y -= self.speed
                if self.direction == "DOWN": self.y += self.speed
            else:
                self.x = center_x
                self.y = center_y

            # transmitir posición
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
                    "is_evil": self.is_evil
                }
                update_object_by_id(peer_players, self.id, msg)
                broadcast_message(packet_data(msg))

        # Animación de la boca
        delta_angle = 8 if self.is_evil else 5  # abre más rápido si es malvado
        if self.mouth_opening:
            self.mouth_angle += delta_angle
            if self.mouth_angle >= 45:
                self.mouth_opening = False
        else:
            self.mouth_angle -= delta_angle
            if self.mouth_angle <= 0:
                self.mouth_opening = True

    def set_position(self, x, y, direction=None, is_evil=None):
        """Actualizar posición desde red"""
        self.x = x
        self.y = y
        if direction:
            self.direction = direction
        if is_evil is not None:
            self.is_evil = is_evil
            self.color = self.evil_color if is_evil else self.base_color

    def draw(self, surface):
        # --- DIBUJAR CUERPO Y BOCA ---
        if self.direction == "RIGHT":
            rotation = 0
        elif self.direction == "LEFT":
            rotation = math.pi
        elif self.direction == "UP":
            rotation = math.pi / 2
        else:
            rotation = -math.pi / 2

        # Cuerpo mantiene su color base
        body_color = self.base_color

        points = [(self.x, self.y)]
        for angle in range(self.mouth_angle, 360 - self.mouth_angle + 1, 5):
            rad = math.radians(angle)
            rx = self.x + self.radius * math.cos(rad + rotation)
            ry = self.y - self.radius * math.sin(rad + rotation)
            points.append((rx, ry))
        pygame.draw.polygon(surface, body_color, points)

        # --- OJOS ---
        eye_offset_x = self.radius * 0.4
        eye_offset_y = -self.radius * 0.5  # siempre arriba

        eye1_pos = (self.x - eye_offset_x, self.y + eye_offset_y)
        eye2_pos = (self.x + eye_offset_x, self.y + eye_offset_y)

        if self.is_evil:
            # Elegir color de ojos malvados que contraste con el cuerpo
            r, g, b = body_color
            # Calcular brillo percibido (según luminancia)
            brightness = (0.299 * r + 0.587 * g + 0.114 * b)
            if brightness > 128:
                evil_eye_color = (180, 0, 0)  # cuerpo claro → ojos rojo oscuro
            elif r > g and r > b:
                evil_eye_color = (0, 255, 255)  # cuerpo rojizo → ojos cian
            elif g > r and g > b:
                evil_eye_color = (255, 0, 255)  # cuerpo verdoso → ojos magenta
            elif b > r and b > g:
                evil_eye_color = (255, 255, 0)  # cuerpo azulado → ojos amarillos
            else:
                evil_eye_color = (255, 0, 0)  # fallback rojo

            # Dibujar ojos y cejas
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
            # ojos normales
            pygame.draw.circle(surface, (0, 0, 0), eye1_pos, 3)
            pygame.draw.circle(surface, (0, 0, 0), eye2_pos, 3)



