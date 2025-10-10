import pygame, random
from p2p_helpers import packet_data
from p2p_node import broadcast_message

class Coin(pygame.sprite.Sprite):
    def __init__(self, pacman, x=0, y=0, frame_rate=100,
                 tile_size=24, board_offset_x=0, board_offset_y=0):
        super().__init__()

        self.pacman = pacman
        self.position = (x, y)
        self.visible = True

        # Parámetros de tablero
        self.tile_size = tile_size
        self.board_offset_x = board_offset_x
        self.board_offset_y = board_offset_y

        # Animación
        self.frames = []
        self.load_frames("images/coin_spritesheet.png")  # tu sprite sheet
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Control de tiempo
        self.frame_rate = frame_rate
        self.last_update = pygame.time.get_ticks()

    def load_frames(self, filename):
        """Carga y corta la hoja de sprites (2 filas × 3 columnas = 6 frames)."""
        sheet = pygame.image.load(filename).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()

        cols, rows = 3, 2
        frame_width = sheet_width // cols
        frame_height = sheet_height // rows

        for row in range(rows):
            for col in range(cols):
                x = col * frame_width
                y = row * frame_height
                frame = sheet.subsurface((x, y, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (self.tile_size, self.tile_size))
                self.frames.append(frame)

    def update(self):
        x,y = self.position
        if x == -10 and y == -10:
            self.visible = False
            return
        else:
            self.visible = True

        """Actualiza la animación."""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def draw(self, surface):
        """Dibuja la moneda en la superficie indicada."""
        if self.visible:
            surface.blit(self.image, self.rect)

    def set_position(self, position):
        self.position = position
        self.rect.topleft = position
        self.pacman.coin_initial_position = position

    def place_random(self, board, player=None):
        """Coloca la moneda en una celda vacía ('0') considerando el offset del tablero."""
        empty_cells = [
            (col_idx, row_idx)
            for row_idx, row in enumerate(board)
            for col_idx, cell in enumerate(row)
            if cell == '0'
        ]
        if not empty_cells:
            print("⚠️ No hay celdas vacías para colocar la moneda.")
            return

        col, row = random.choice(empty_cells)
        pos = (
            self.board_offset_x + col * self.tile_size,
            self.board_offset_y + row * self.tile_size
        )

        self.pacman.coin_initial_position = pos
        self.rect.topleft = pos
        self.position = pos

        # inform the new position
        try:
            cx, cy = pos
            msg =  {
                "id": "server",
                "from": "server",
                "coin_position": f"{cx},{cy}",
                "outgoing_player": False
            }
            pkt = packet_data(msg)
            broadcast_message(pkt)
        except Exception as e:
            print(e)
