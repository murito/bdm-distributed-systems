import json
import time

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

    def update(self, keys, board):
        rows = len(board)
        cols = len(board[0])

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

            # transmit position here
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
                    "coin_initial_position": f"{cx},{cy}"
                }
                update_object_by_id(peer_players, self.id, msg)
                broadcast_message(packet_data(msg))

        # Animación de la boca
        if self.mouth_opening:
            self.mouth_angle += 5
            if self.mouth_angle >= 45:
                self.mouth_opening = False
        else:
            self.mouth_angle -= 5
            if self.mouth_angle <= 0:
                self.mouth_opening = True

    def set_position(self, x, y, direction=None):
        """Actualizar posición desde red"""
        self.x = x
        self.y = y
        if direction:
            self.direction = direction

    def draw(self, surface):
        if self.direction == "RIGHT":
            rotation = 0
        elif self.direction == "LEFT":
            rotation = math.pi
        elif self.direction == "UP":
            rotation = math.pi / 2
        else:
            rotation = -math.pi / 2

        points = [(self.x, self.y)]
        for angle in range(self.mouth_angle, 360 - self.mouth_angle + 1, 5):
            rad = math.radians(angle)
            rx = self.x + self.radius * math.cos(rad + rotation)
            ry = self.y - self.radius * math.sin(rad + rotation)
            points.append((rx, ry))
        pygame.draw.polygon(surface, self.color, points)